from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Liquidation(models.Model):
    _name = 'shrimp_liquidation.liquidation'
    _description = 'Liquidation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # @api.model
    # def _get_default_location_src_id_config(self):
    #     config_param = self.env['ir.config_parameter'].sudo().get_param('shrimp_liquidation.liquidation_location_src_id')
    #     return self.env['stock.location'].browse(int(config_param)).id if config_param else False

    @api.model
    def _get_default_picking_type(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        return self.env['stock.picking.type'].search([('code', '=', 'liquidation'),
                                                      ('warehouse_id.company_id', '=', company_id)
                                                      ], limit=1).id

    def _get_default_classified_pounds_uom(self):
        return self.env['uom.uom'].search([('name', '=', 'lb')], limit=1).id

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

    process = fields.Selection([
        ('full', 'Entero'),
        ('shell_on', 'Colas'),
        ('pcd_iqf', 'PCD IQF'),
        ('cooked_pyd', 'Cocido PYD IQF'),
        ('pyd_block', 'PYD BLOQUE'),
    ], string="Proceso")

    name = fields.Char(string='Name', readonly=True, required=True, copy=False, default='New')
    sequence = fields.Char(string='Sequence', readonly=True)

    is_reprocess = fields.Boolean(string="Reproceso")
    is_fresh = fields.Boolean(string="Fresco")

    # Header
    process_plant = fields.Char(string="Planta de proceso")
    provider_id = fields.Many2one('res.partner', string="Proveedor", required=True)
    reported_pounds = fields.Float(string="Libras reportadas", required=True)
    classified_pounds = fields.Float(string="Libras clasificadas", compute="_compute_classified_pounds", required=True)
    classified_uom = fields.Many2one('uom.uom', string="UdM", default=_get_default_classified_pounds_uom)

    reception_date = fields.Date(string="Fecha de recepción")
    received_pounds = fields.Float(string="Libras recibidas")
    batch_number = fields.Char(string="Número de lote")

    # Shrimp classification
    liquidity_lines_ids = fields.One2many('shrimp_liquidation.liquidation.line', 'liquidation_id',
                                          string="Líneas de producto empaquetado")
    total_packaged_weight = fields.Float(string="Peso total empaquetado", compute="_compute_total_packaged_weight")
    shrimps_purchase_order_id = fields.Many2one('purchase.order', string="Orden de compra de camarón", copy=False)

    # Information
    client = fields.Many2one('res.partner', string="Cliente")
    production_order = fields.Char(string="Orden de producción")
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
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company, required=True)

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
        ('classified', 'Clasificado'),
        ('confirm_materials', 'Materiales confirmados'),
        ('consume_materials', 'Materiales consumidos'),
        ('used_services', 'Ordenes de Servicios'),
        ('done', 'Realizado'),
    ], string='Estado', default='draft')

    # Material movements
    move_material_ids = fields.One2many('stock.move', 'liquidation_id', string="Movimientos")
    location_src_id = fields.Many2one(
        'stock.location', 'Components Location',
        default=lambda self: self.env.company.liquidation_location_src_id.id or False,
        readonly=True,
        required=True,
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
        help="Location where the system will look for materials.")

    material_location_id = fields.Many2one('stock.location', "Materials Location",
                                           compute="_compute_production_location", store=True)
    reserve_visible = fields.Boolean(compute='_compute_unreserve_visible')
    unreserve_visible = fields.Boolean(compute='_compute_unreserve_visible')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True,
                                      default=_get_default_picking_type, check_company=True,
                                      domain="[('code', '=', 'liquidation'), ('company_id', '=', company_id)]")

    # Services
    service_lines_ids = fields.One2many('shrimp_liquidation.liquidation.service.line', 'liquidation_id',
                                        string="Líneas de servicios")

    service_order_ids = fields.One2many('purchase.order', 'service_liquidation_id', string="Ordenes de servicio", copy=False)
    service_count = fields.Integer(string="Servicios", compute="_compute_service_count")
    landing_cost_id = fields.Many2one('stock.landed.cost', string="Costos de aterrizaje", copy=False)
    landing_cost_account = fields.Many2one('account.account', string="Cuenta de costos de aterrizaje", copy=False)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('shrimp_liquidation.liquidation.sequence') or _('New')
        return super(Liquidation, self).create(vals)

    @api.onchange('process')
    def _onchange_process(self):
        services_handler = {
            'shell_on': self.env.company.shellon_service_ids,
            'full': self.env.company.whole_shrimp_service_ids,
            'pcd_iqf': self.env.company.pcd_iqf_service_ids,
            'cooked_pyd': self.env.company.cooked_pyd_service_ids,
            'pyd_block': self.env.company.pyd_block_service_ids,
        }
        services = services_handler.get(self.process)
        if services:
            self.service_lines_ids = [(5, 0, 0)]
            for service in services:
                self.service_lines_ids = [(0, 0, {
                    'liquidation_id': self.id,
                    'product_service_id': service.id,
                    'provider_id': service.seller_ids.name.id,
                })]

    @api.depends('liquidity_lines_ids')
    def _compute_total_packaged_weight(self):
        for r in self:
            r.total_packaged_weight = sum(r.liquidity_lines_ids.mapped('total_uom_weight'))

    @api.depends('liquidity_lines_ids')
    def _compute_classified_pounds(self):
        for r in self:
            classified_pounds = sum(r.liquidity_lines_ids.mapped('total_uom_weight'))
            if classified_pounds > r.received_pounds:
                raise UserError(_("Las libras clasificadas no pueden ser mayores a las libras recibidas."))
            r.classified_pounds = classified_pounds

    def generate_purchase_order(self):
        self.write({'state': 'classified'})
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.provider_id.id,
            'liquidation_id': self.id,
            'date_order': fields.Datetime.now(),
            'date_planned': fields.Datetime.now(),
        })

        for line in self.liquidity_lines_ids:
            self.env['purchase.order.line'].create({
                'product_id': line.product_id.id,
                'product_qty': line.total_uom_weight,
                'price_unit': line.product_unit_cost,
                'order_id': purchase_order.id,
                'product_uom': line.product_id.uom_po_id.id,
            })

        self.write({'shrimps_purchase_order_id': purchase_order.id})
        # Post a message in the chatter with the generated PO
        self.message_post(
            body=_("Orden de compra <a href=# data-oe-model=purchase.order data-oe-id=%d>%s</a> ha sido generada.") % (
                purchase_order.id, purchase_order.name))
        self.message_post(body=_("Estado: Borrador -> Orden Creada"))

    def action_view_shrimp_order(self):
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        action['res_id'] = self.shrimps_purchase_order_id.id
        return action

    def action_view_services(self):
        # This functionn returns an action that display existing purchase orders of services for current liquidation.
        # If only 1 record exists, show the form view directly
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        if len(self.service_order_ids) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = self.service_order_ids.id
        else:
            action['domain'] = [('id', 'in', self.service_order_ids.ids)]

        return action

    def action_generate_landing_costs(self):
        if not self.landing_cost_account:
            raise UserError(_('No se ha configurado la cuenta de costos de aterrizaje.'))

        if not self.shrimps_purchase_order_id.picking_ids:
            raise UserError(_('No se ha creado la orden de recepcion'))

        # Check if picking state is done
        if self.shrimps_purchase_order_id.picking_ids.state != 'done':
            raise UserError(_('No se ha completado la orden de recepcion'))

        landed_cost = self.env['stock.landed.cost'].create({
            'picking_ids': [(6, 0, self.shrimps_purchase_order_id.picking_ids.ids)],
            'liquidation_id': self.id,
        })
        # Fill the cost_lines with the products that are used in the services_lines_ids
        for line in self.service_lines_ids:
            landed_cost.write({
                'cost_lines': [(0, 0, {
                    'product_id': line.product_service_id.id,
                    'name': line.product_service_id.name,
                    'split_method': 'by_quantity',
                    'price_unit': line.service_unit_cost,
                    'account_id': self.landing_cost_account.id,
                })]
            })

        for material_line in self.move_material_ids:
            landed_cost.write({
                'cost_lines': [(0, 0, {
                    'product_id': material_line.product_id.id,
                    'name': material_line.product_id.name,
                    'split_method': 'by_quantity',
                    'price_unit': material_line.product_unit_price * material_line.product_uom_qty,
                    'account_id': self.landing_cost_account.id,
                })]
            })

        landed_cost.compute_landed_cost()
        self.write({'landing_cost_id': landed_cost.id})
        self.write({'state': 'done'})

    def action_view_landing_costs(self):
        # The .read()[0] method is then called to retrieve the dictionary representation of the action's definition,
        # and select the first (and only) element of the resulting list.
        action = self.env.ref('stock_landed_costs.action_stock_landed_cost').read()[0]
        # Open the form view of the landed cost
        action['views'] = [(self.env.ref('stock_landed_costs.view_stock_landed_cost_form').id, 'form')]
        # Specify the ID of the landed cost to open
        action['res_id'] = self.landing_cost_id.id
        return action

    def _compute_service_count(self):
        for record in self:
            record.service_count = len(record.service_order_ids)

    def action_draft(self):
        self.state = 'draft'

    def action_assign(self):
        for liquidation in self:
            liquidation.move_material_ids._action_assign()
        return True

    def do_unreserve(self):
        self.move_material_ids.filtered(lambda x: x.state not in ('done', 'cancel'))._do_unreserve()
        return True

    def action_unreserve(self):
        self.ensure_one()
        self.do_unreserve()
        return True

    def action_confirm(self):
        if not self.move_material_ids:
            raise UserError(_('No se ha agregado ningún material a la liquidación.'))
        self.state = 'confirm_materials'
        for liquidation in self:
            liquidation.move_material_ids._action_confirm(merge=False)
        return True

    def action_done(self):
        res = self._pre_mark_done()
        if res is not True:
            return res

        liquidations_not_to_backorder = self
        liquidations_not_to_backorder._post_inventory()

        self.write({'state': 'consume_materials'})
        self.message_post(body=_("Estado: Confirmado -> Realizado"))
        self.message_post(body=_("Materiales consumidos"))

    def _post_inventory(self):
        for order in self:
            moves_not_to_do = order.move_material_ids.filtered(lambda x: x.state == 'done')
            moves_to_do = order.move_material_ids.filtered(lambda x: x.state not in ('done', 'cancel'))

            moves_to_do._action_done()
            moves_to_do = order.move_material_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do

            consumed_moves_lines = moves_to_do.mapped('move_line_ids')
            order.move_material_ids.move_line_ids.consume_line_ids = [(6, 0, consumed_moves_lines.ids)]

        return True

    def _pre_mark_done(self):
        for liquidation in self:
            if not any(liquidation.move_material_ids.mapped('quantity_done')):
                raise UserError(_('No se puede marcar como realizado una liquidación sin consumir materiales.'))

        return True

    @api.depends('move_material_ids', 'state', 'move_material_ids.product_uom_qty')
    def _compute_unreserve_visible(self):
        for liquidation in self:
            already_reserved = liquidation.state not in ('done') and liquidation.mapped('move_material_ids.move_line_ids')
            any_quantity_done = any(move.quantity_done > 0 for move in liquidation.move_material_ids)

            liquidation.unreserve_visible = not any_quantity_done and already_reserved
            liquidation.reserve_visible = liquidation.state in ('confirm_materials') and any(move.product_uom_qty and move.state in ['confirmed', 'partially_available'] for move in liquidation.move_material_ids)

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        self.move_material_ids.update({'picking_type_id': self.picking_type_id})

    def action_generate_services(self):
        if not self.service_lines_ids:
            raise UserError(_('No se ha agregado ningún servicio.'))

        self.write({'state': 'used_services'})
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

            self.service_order_ids = [(4, purchase_order.id)]

            # Post a message in the chatter with the generated PO
            self.message_post(
                body=_(
                    "Orden de compra <a href=# data-oe-model=purchase.order data-oe-id=%d>%s</a> ha sido generada.") % (
                         purchase_order.id, purchase_order.name))
            self.message_post(body=_("Estado: PO de Servicios Creada"))
