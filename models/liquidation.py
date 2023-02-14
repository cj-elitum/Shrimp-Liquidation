from odoo import models, fields, api, _


class Liquidation(models.Model):
    _name = 'shrimp_liquidation.liquidation'
    _description = 'Liquidation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_default_location_src_id(self):
        location = False
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        if self.env.context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(
                self.env.context['default_picking_type_id']).default_location_src_id
        if not location:
            location = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
        return location and location.id or False

    @api.model
    def _get_default_location_dest_id(self):
        location = False
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(
                self.env.context['default_picking_type_id']).default_location_dest_id
        if not location:
            location = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
        return location and location.id or False

    @api.depends('company_id')
    def _compute_production_location(self):
        if not self.company_id:
            return
        location_by_company = self.env['stock.location'].read_group([
            ('company_id', 'in', self.company_id.ids),
            ('usage', '=', 'production')
        ], ['company_id', 'ids:array_agg(id)'], ['company_id'])
        location_by_company = {lbc['company_id'][0]: lbc['ids'] for lbc in location_by_company}
        for liquidation in self:
            liquidation.material_location_id = location_by_company.get(liquidation.company_id.id)[0]

    name = fields.Char(string='Name', required=True)
    process = fields.Selection([
        ('shell_on', 'Colas'),
        ('pcd_iqf', 'PCD IQF'),
        ('cooked_pyd', 'Cocido PYD IQF'),
        ('pyd_block', 'PYD BLOQUE'),
        ('fresh', 'Frescos'),
    ], string="Proceso")

    is_reprocess = fields.Boolean(string="REPROCESOS")

    # Header
    proccess_plant = fields.Char(string="Planta de proceso")
    provider_id = fields.Many2one('res.partner', string="Proveedor", required=True)
    reported_pounds = fields.Float(string="Libras reportadas")
    classified_pounds = fields.Float(string="Libras clasificadas", compute="_compute_classified_pounds")
    reception_date = fields.Date(string="Fecha de recepción")
    received_pounds = fields.Float(string="Libras recibidas")
    batch_number = fields.Char(string="Número de lote")

    # Packaged Product Lines
    liquidity_lines_ids = fields.One2many('shrimp_liquidation.liquidation.line', 'liquidation_id',
                                          string="Líneas de producto empaquetado")
    total_packaged_weight = fields.Float(string="Peso total empaquetado", compute="_compute_total_packaged_weight")
    purchase_order_ids = fields.One2many('purchase.order', 'liquidation_id', string="Ordenes de compra")

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
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

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

    # State
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('order_created', 'Orden Creada'),
        ('validated_materials', 'Materiales Validados'),
    ], string='Estado', default='draft')

    # Materials
    material_lines_ids = fields.One2many('shrimp_liquidation.material.line', 'liquidation_id',
                                         string="Líneas de materiales")

    # Material movements
    move_material_ids = fields.One2many('stock.move', 'liquidation_id', string="Movimientos")
    location_src_id = fields.Many2one(
        'stock.location', 'Components Location',
        default=_get_default_location_src_id,
        readonly=True, required=True,
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]}, check_company=True,
        help="Location where the system will look for components.")

    material_location_id = fields.Many2one('stock.location', "Materials Location",
                                           compute="_compute_production_location", store=True)

    # Services
    service_lines_ids = fields.One2many('shrimp_liquidation.liquidation.service.line', 'liquidation_id',
                                        string="Líneas de servicios")

    @api.depends('liquidity_lines_ids')
    def _compute_total_packaged_weight(self):
        for r in self:
            r.total_packaged_weight = sum(r.liquidity_lines_ids.mapped('total_weight'))

    @api.depends('liquidity_lines_ids')
    def _compute_classified_pounds(self):
        for r in self:
            r.classified_pounds = sum(r.liquidity_lines_ids.mapped('total_weight'))

    def generate_purchase_order(self):
        self.write({'state': 'order_created'})
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.provider_id.id,
            'liquidation_id': self.id,
            'date_order': fields.Datetime.now(),
            'date_planned': fields.Datetime.now(),
        })

        for line in self.liquidity_lines_ids:
            self.env['purchase.order.line'].create({
                'product_id': line.product_id.id,
                'product_qty': line.total_weight,
                'price_unit': line.product_id.standard_price,
                'order_id': purchase_order.id,
                'product_uom': line.product_id.uom_po_id.id,
            })
        # Post a message in the chatter with the generated PO
        self.message_post(
            body=_("Orden de compra <a href=# data-oe-model=purchase.order data-oe-id=%d>%s</a> ha sido generada.") % (
                purchase_order.id, purchase_order.name))
        self.message_post(body=_("Estado: Borrador -> Orden Creada"))

    def action_draft(self):
        self.state = 'draft'

    def action_validate_materials(self):
        self.state = 'validated_materials'

    def action_generate_services(self):
        for service in self.service_lines_ids:
            purchase_order = self.env['purchase.order'].create({
                'partner_id': service.provider_id.id,
                'liquidation_id': self.id,
                'date_order': fields.Datetime.now(),
                'date_planned': fields.Datetime.now(),
            })

            self.env['purchase.order.line'].create({
                'product_id': service.product_service_id.id,
                'product_qty': service.service_qty,
                'order_id': purchase_order.id,
            })

            # Post a message in the chatter with the generated PO
            self.message_post(
                body=_(
                    "Orden de compra <a href=# data-oe-model=purchase.order data-oe-id=%d>%s</a> ha sido generada.") % (
                         purchase_order.id, purchase_order.name))
            self.message_post(body=_("Estado: PO de Servicios Creada"))





