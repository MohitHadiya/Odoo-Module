from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_date = fields.Date()
