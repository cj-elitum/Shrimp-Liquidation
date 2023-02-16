from odoo import models, fields, api


class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = 'stock.move'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion", ondelete='cascade')

    def action_show_details(self):
        self.ensure_one()
        action = super(StockMove, self).action_show_details()
        if self.liquidation_id:
            action['context']['show_destination_location'] = False
        return action
