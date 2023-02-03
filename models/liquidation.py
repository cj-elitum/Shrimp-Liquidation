from odoo import models, fields, api


class Liquidation(models.Model):
    _name = 'shrimp_liquidation.liquidation'
    _description = 'Liquidation'

    name = fields.Char(string='Name', required=True)

    cola = fields.Boolean(string="COLA")
    pcd_iqf = fields.Boolean(string="PCD IQF")
    cocido_pyd_iqf = fields.Boolean(string="COCIDO PYD IQF")
    pyd_block = fields.Boolean(string="PYD BLOQUE")
    fresh = fields.Boolean(string="FRESCOS")
    reprocesses = fields.Boolean(string="REPROCESOS")

    # Header
    proccess_plant = fields.Char(string="Planta de proceso")
    provider = fields.Many2one('res.partner', string="Proveedor")
    reported_pounds = fields.Float(string="Libras reportadas")
    classified_pounds = fields.Float(string="Libras clasificadas")
    reception_date = fields.Date(string="Fecha de recepción")
    received_pounds = fields.Float(string="Libras recibidas")
    batch_number = fields.Char(string="Número de lote")

    # Packaged Product Lines
    liquidity_lines_ids = fields.One2many('shrimp_liquidation.liquidation.line', 'liquidation_id', string="Líneas de producto empaquetado")
    total_packaged_weight = fields.Float(string="Peso total empaquetado", compute="_compute_total_packaged_weight")

    # Information
    client = fields.Many2one('res.partner', string="Cliente")
    production_order = fields.Char(string="Orden de producción")
    batch_amount = fields.Integer(string="Cantidad de lote")
    expenses = fields.Float(string="Egresos")
    final_batch = fields.Char(string="Lote final")
    damaged_product = fields.Float(string="Material dañado")
    product_for_process = fields.Float(string="Producto para proceso")
    frozen_product = fields.Float(string="Congelado")
    fresh_product = fields.Float(string="Fresco")
    discharge_date = fields.Date(string="Fecha de descarga de camara")
    entry_date = fields.Date(string="Fecha de entrada de camara")
    process_date = fields.Date(string="Fecha de proceso")
    process_days = fields.Integer(string="Días de proceso")
    requested_glazing_qty = fields.Float(string="% de glaseado solicitada")
    glazing_qty = fields.Float(string="% de glaseado real")
    thawing_period_start_datetime = fields.Datetime(string="Inicio de periodo de descongelación")
    thawing_period_end_datetime = fields.Datetime(string="Fin de periodo de descongelación")

    # Rendimiento
    peeled_pounds = fields.Float(string="Libras peladas")
    treated_pounds = fields.Float(string="Libras tratadas")
    cooked_pounds = fields.Float(string="Libras cocidas")
    decorated_pounds = fields.Float(string="Libras decoradas")
    pound_before_glazing = fields.Float(string="Libras antes de glaseado")
    packaged_pounds = fields.Float(string="Libras empaquetadas")
    peeling_yield = fields.Float(string="Rendimiento de pelado")
    treated_yield = fields.Float(string="Rendimiento de tratado")
    cooked_yield = fields.Float(string="Rendimiento del cocido")
    decorated_yield = fields.Float(string="Rendimiento del decorado")
    iqf_yield = fields.Float(string="Rendimiento del IQF")
    cola_pounds_yield = fields.Float(string="Rendimiento de Libras COLA")

    # Materials
    material_lines_ids = fields.One2many('shrimp_liquidation.material.line', 'liquidation_id', string="Líneas de materiales")

    @api.depends('liquidity_lines_ids')
    def _compute_total_packaged_weight(self):
        for r in self:
            r.total_packaged_weight = sum(r.liquidity_lines_ids.mapped('total_weight'))





