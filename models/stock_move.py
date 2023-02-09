from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion", ondelete='cascade')

