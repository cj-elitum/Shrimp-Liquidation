from odoo import models, fields, api


class LiquidationServiceLine(models.Model):
    _name = 'shrimp_liquidation.liquidation.service.line'
    _description = 'Liquidation Service Line'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion")
    product_service_id = fields.Many2one('product.product', string="Servicio", domain=[('type', '=', 'service')])
    service_qty = fields.Integer(string="Cantidad")
    provider_id = fields.Many2one('res.partner', string="Proveedor")
    service_unit_cost = fields.Float(string="Costo unitario", related="product_service_id.standard_price")

    @api.onchange('product_service_id')
    def _onchange_product_id(self):
        providers = self.product_service_id.seller_ids.mapped('name')
        self.provider_id = False
        return {'domain': {'provider_id': [('id', 'in', providers.ids)]}}
