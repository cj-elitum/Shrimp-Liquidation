from odoo import models, fields, api


class LiquidationLine(models.Model):
    _name = 'shrimp_liquidation.liquidation.line'
    _description = 'Package Line'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion")
    product_template_id = fields.Many2one('product.template', string="Producto")
    size = fields.Char(related='product_template_id.size', string="Talla")
    product_unit_cost = fields.Float(related='product_template_id.standard_price', string="Costo Unitario")

    package_type = fields.Selection([
        ('6x2 kg', '6x2 kg'),
        ('grilla', 'Grilla'),
        ('3QF', '3QF'),
    ], string="Empaque")
    qty = fields.Float(string="Cantidad")
    weight = fields.Float(string="Peso")
    total_weight = fields.Float(string="Total")



