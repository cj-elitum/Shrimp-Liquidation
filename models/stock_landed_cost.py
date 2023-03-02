from odoo import models, fields, api

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidación", ondelete='cascade')

