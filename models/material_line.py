from odoo import models, fields, api


class MaterialLine(models.Model):
    _name = 'shrimp_liquidation.material.line'
    _description = 'Material Line'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion")
    product_template_id = fields.Many2one('product.template', string="Empaque", domain=[('purchase_ok', '=', True),('categ_id.name', '=', 'Materiales')])
    product_unit_cost = fields.Float(related='product_template_id.standard_price', string="Costo Unitario")
    qty = fields.Float(string="Cantidad")