from odoo import models, fields, api


class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = 'stock.move'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion", ondelete='cascade')

    # def _search_picking_for_assignation_domain(self):
    #     if self.liquidation_id:
    #         res = super(StockMove, self)._search_picking_for_assignation_domain()
    #         res += [('origin', '=', self.liquidation_id.name)]
    #     return res


    def action_show_details(self):
        self.ensure_one()
        action = super(StockMove, self).action_show_details()
        if self.liquidation_id:
            action['context']['show_destination_location'] = False
        return action

    @api.model
    def _consuming_picking_types(self):
        res = super()._consuming_picking_types()
        res.append('liquidation')
        return res
