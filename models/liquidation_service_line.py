from odoo import models, fields, api


class LiquidationServiceLine(models.Model):
    _name = 'shrimp_liquidation.liquidation.service.line'
    _description = 'Liquidation Service Line'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion")
    product_service_id = fields.Many2one('product.product', string="Servicio", domain=[('type', '=', 'service')])
    service_qty = fields.Integer(string="Cantidad")
    provider_id = fields.Many2one('res.partner', string="Proveedor")
