from odoo import models, fields, api

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidación", ondelete='cascade')
    landed_cost_total = fields.Float(string="Costo adicional total", compute="_compute_landed_cost_total", store=True, readonly=True)

    @api.depends('valuation_adjustment_lines')
    def _compute_landed_cost_total(self):
        for record in self:
            record.landed_cost_total = sum(record.valuation_adjustment_lines.mapped('additional_landed_cost'))