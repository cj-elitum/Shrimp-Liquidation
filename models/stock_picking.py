from odoo import fields, models, api

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection(selection_add=[
        ('liquidation', 'Liquidation')
    ], ondelete={'liquidation': 'cascade'})

