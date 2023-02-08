from odoo import models, fields, api


class LiquidationLine(models.Model):
    _name = 'shrimp_liquidation.liquidation.line'
    _description = 'Package Line'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Producto", domain=[('purchase_ok', '=', True),('categ_id.name', '=', 'Camaron')])
    product_unit_cost = fields.Float(string="Costo unitario", related="product_id.standard_price")
    product_uom = fields.Many2one('uom.uom', string="UoM", related="product_id.uom_id")
    package_id = fields.Many2one('shrimp_liquidation.liquidation.package', string="Empaque")

    qty = fields.Integer(string="Cantidad")
    weight = fields.Float(string="Peso")
    total_weight = fields.Float(string="Peso total", compute="_compute_total_weight", store=True, readonly=True)

    @api.depends('qty', 'weight')
    def _compute_total_weight(self):
        for record in self:
            record.total_weight = record.qty * record.weight

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.qty = 1




