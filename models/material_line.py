from odoo import models, fields, api


class MaterialLine(models.Model):
    _name = 'shrimp_liquidation.material.line'
    _description = 'Material Line'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion")
    product_shrimp_id = fields.Many2one('product.template', string="Camaron",
                                        domain=[('purchase_ok', '=', True), ('categ_id.name', '=', 'Camaron')])

    # Packages
    product_package_id = fields.Many2one('product.template', string="Empaques",
                                         domain=[('purchase_ok', '=', True), ('categ_id.name', '=', 'Empaques')])
    package_qty = fields.Float(string="Cantidad")
    product_package_uom = fields.Many2one('uom.uom', string="UoM", related="product_package_id.uom_id")
    package_stock_availability = fields.Float(string="Disponibilidad", compute="_compute_stock_availability", readonly=True)


    # Materials
    product_material_id = fields.Many2one('product.template', string="Materiales",
                                          domain=[('purchase_ok', '=', True), ('categ_id.name', '=', 'Materiales')])
    material_qty = fields.Integer(string="Cantidad")
    product_material_uom = fields.Many2one('uom.uom', string="UoM", related="product_material_id.uom_id")
    material_stock_availability = fields.Float(string="Disponibilidad", compute="_compute_stock_availability", readonly=True)

    @api.depends('product_package_id')
    def _compute_stock_availability(self):
        for record in self:
            stock_quant = self.env['stock.quant'].search(
                [('product_id', '=', record.product_package_id.product_variant_id.id)], limit=1)
            record.package_stock_availability = stock_quant.quantity

            stock_quant = self.env['stock.quant'].search(
                [('product_id', '=', record.product_material_id.product_variant_id.id)], limit=1)
            record.material_stock_availability = stock_quant.quantity

    @api.onchange('qty')
    def _onchange_qty(self):
        if self.qty > self.package_stock_availability:
            self.qty = self.package_stock_availability
            # Return and display a warning message
            return {
                'warning': {
                    'title': "Cantidad excede la disponibilidad",
                    'message': "La cantidad excede la disponibilidad en stock",
                }
            }

