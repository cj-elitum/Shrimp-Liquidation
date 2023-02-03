from odoo import models, fields, api


class MaterialLine(models.Model):
    _name = 'shrimp_liquidation.material.line'
    _description = 'Material Line'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion")
    product_template_id = fields.Many2one('product.template', string="Empaque")
    product_unit_cost = fields.Float(related='product_template_id.standard_price', string="Costo Unitario")
    size = fields.Char(related='product_template_id.size', string="Talla")
    package_type = fields.Selection([
        ('funda', 'Fundas'),
        ('master', 'Master'),
    ], string="Empaque")
    lbs_iqf = fields.Float(string="Lbs IQF")
    qty = fields.Float(string="Cantidad")
    weight = fields.Float(string="Peso")
    total_weight = fields.Float(string="Total")