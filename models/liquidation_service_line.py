import json

from odoo import models, fields, api


class LiquidationServiceLine(models.Model):
    _name = 'shrimp_liquidation.liquidation.service.line'
    _description = 'Liquidation Service Line'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion")
    product_service_id = fields.Many2one('product.product', string="Servicio", domain=[('type', '=', 'service')])
    service_qty = fields.Integer(string="Cantidad", default=1)
    provider_id_domain = fields.Char(compute="_compute_provider_id_domain", store=True, readonly=True)
    provider_id = fields.Many2one('res.partner', string="Proveedor")
    service_unit_cost = fields.Float(string="Costo unitario", required=True, default=lambda self: self.product_service_id.standard_price)

    @api.onchange('product_service_id')
    def _onchange_product_id(self):
        providers = self.product_service_id.seller_ids.mapped('name')
        self.provider_id = False
        return {'domain': {'provider_id': [('id', 'in', providers.ids)]}}

    @api.onchange('provider_id')
    def _onchange_provider_id(self):
        self.service_unit_cost = self.product_service_id.seller_ids.filtered(lambda r: r.name == self.provider_id).price

    @api.depends('product_service_id')
    def _compute_provider_id_domain(self):
        for record in self:
            providers = record.product_service_id.seller_ids.mapped('name')
            record.provider_id_domain = json.dumps([('id', 'in', providers.ids)])
