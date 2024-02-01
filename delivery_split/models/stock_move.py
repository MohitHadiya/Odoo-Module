# -*- coding: utf-8 -*-
from odoo import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        picking_dict = super()._get_new_picking_values()
        if self.sale_line_id:
            picking_dict['delivery_date'] = self.sale_line_id[0].delivery_date
        return picking_dict

    def _search_picking_for_assignation_domain(self):
        domain = super()._search_picking_for_assignation_domain()
        if self.sale_line_id:
            domain.append(('delivery_date', '=', self.sale_line_id.delivery_date))
        return domain
