from odoo import models, fields, api


class LiquidationLine(models.Model):
    _name = 'shrimp_liquidation.liquidation.line'
    _description = 'Package Line'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidacion", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Producto", required=True)
    suitable_product_ids = fields.Many2many('product.product', compute="_compute_suitable_product_ids")
    product_unit_cost = fields.Float(string="Costo unitario", readonly=True)
    product_uom = fields.Many2one('uom.uom', string="Unidad de medida")
    package_id = fields.Many2one('shrimp_liquidation.liquidation.package', string="Empaque")
    product_attribute_ids = fields.Many2many('product.template.attribute.value', string="Atributos",
                                             related="product_id.product_template_attribute_value_ids")
    qty = fields.Integer(string="Cantidad")
    weight = fields.Float(string="Peso")
    total_weight = fields.Float(string="Peso total", compute="_compute_total_weight", store=True, readonly=True)
    total_uom_weight = fields.Float(string="Cantidad convertida", compute="_compute_total_uom_weight", readonly=True)
    product_po_uom = fields.Many2one('uom.uom', string="UdM", related="product_id.uom_po_id")

    @api.depends('qty', 'weight')
    def _compute_total_weight(self):
        for record in self:
            record.total_weight = record.qty * record.weight

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        self.product_uom = self.product_id.uom_po_id
        self._suggest_quantity()
        self._onchange_total_weight()

    def _onchange_total_weight(self):
        if not self.product_id:
            return
        # Get the provider
        seller = self.product_id._select_seller(
            partner_id=self.liquidation_id.provider_id,
            quantity=self.total_weight,
            uom_id=self.product_uom,
        )
        self.product_unit_cost = seller.price

    def _suggest_quantity(self):
        if not self.product_id:
            return
        seller_min_qty = self.product_id.seller_ids\
            .filtered(lambda r: r.name == self.liquidation_id.provider_id and (not r.product_id or r.product_id == self.product_id))\
            .sorted(key=lambda r: r.min_qty)
        if seller_min_qty:
            self.qty = seller_min_qty[0].min_qty or 1.0
            self.weight = 1.0
        else:
            self.qty = 1.0
            self.weight = 1.0

    @api.depends('product_uom', 'total_weight', 'product_id.uom_id')
    def _compute_total_uom_weight(self):
        rounding_method = 'HALF-UP'
        for line in self:
            if line.product_id and line.product_id.uom_id != line.product_uom:
                line.total_uom_weight = line.product_uom._compute_quantity(line.total_weight, line.product_id.uom_po_id, rounding_method=rounding_method)
            else:
                line.total_uom_weight = line.total_weight

    @api.depends('liquidation_id.process')
    def _compute_suitable_product_ids(self):
        for line in self:
            process_type = line.liquidation_id.process
            line.suitable_product_ids = self.env['product.product'].search([('process_type', '=', process_type)])
