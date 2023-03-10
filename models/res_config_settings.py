from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Liquidation
    liquidation_location_src_id = fields.Many2one('stock.location', 'Source Location', related='company_id.liquidation_location_src_id', readonly=False)
    shellon_service_ids = fields.Many2many('product.product', 'shellon_service_rel', string='Shellon Services', related='company_id.shellon_service_ids', readonly=False, domain=[('type', '=', 'service')])


class ResCompany(models.Model):
    _inherit = 'res.company'

    liquidation_location_src_id = fields.Many2one('stock.location', 'Source Location')
    shellon_service_ids = fields.Many2many('product.product', 'shellon_service_rel', string='Shellon Services', domain=[('type', '=', 'service')])



