# -*- coding: utf-8 -*-

from odoo.tools import float_compare

from odoo import models, fields
from odoo.tools.misc import clean_context, OrderedSet, groupby


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delivery_date = fields.Date()

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        # Override this method to split the delivery order based on the date mentioned in the sale order line.
        if self._context.get("skip_procurement"):
            return True
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for delivery_date, lines in groupby(self, key=lambda m: m.delivery_date):
            # Here the sale line is groupby based on the delivery date
            procurements = []
            for line in lines:
                line = line.with_company(line.company_id)
                if line.state != 'sale' or not line.product_id.type in ('consu', 'product'):
                    continue
                qty = line._get_qty_procurement(previous_product_uom_qty)
                if float_compare(qty, line.product_uom_qty, precision_digits=precision) == 0:
                    continue

                group_id = line._get_procurement_group()
                if not group_id:
                    group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                    line.order_id.procurement_group_id = group_id
                else:
                    # In case the procurement group is already created and the order was
                    # cancelled, we need to update certain values of the group.
                    updated_vals = {}
                    if group_id.partner_id != line.order_id.partner_shipping_id:
                        updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                    if group_id.move_type != line.order_id.picking_policy:
                        updated_vals.update({'move_type': line.order_id.picking_policy})
                    if updated_vals:
                        group_id.write(updated_vals)

                values = line._prepare_procurement_values(group_id=group_id)
                product_qty = line.product_uom_qty - qty

                line_uom = line.product_uom
                quant_uom = line.product_id.uom_id
                product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
                procurements.append(self.env['procurement.group'].Procurement(
                    line.product_id, product_qty, procurement_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.product_id.display_name, line.order_id.name, line.order_id.company_id, values))
            if procurements:
                procurement_group = self.env['procurement.group']
                if self.env.context.get('import_file'):
                    procurement_group = procurement_group.with_context(import_file=False)
                procurement_group.run(procurements)

        # This next block is currently needed only because the scheduler trigger is done by picking confirmation rather than stock.move confirmation
        orders = self.mapped('order_id')
        for order in orders:
            pickings_to_confirm = order.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
            if pickings_to_confirm:
                # Trigger the Scheduler for Pickings
                pickings_to_confirm.action_confirm()
        return True
