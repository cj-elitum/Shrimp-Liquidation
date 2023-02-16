from odoo import models, fields, api


class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = 'stock.move'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion", ondelete='cascade')

    # def _show_details_in_draft(self):
    #     self.ensure_one()
    #     if self.liquidation_id and self.liquidation_id.state != 'draft':
    #         return True
    #     else:
    #         return super()._show_details_in_draft()
