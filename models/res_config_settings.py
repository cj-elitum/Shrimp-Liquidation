from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Liquidation
    liquidation_location_src_id = fields.Many2one('stock.location', 'Source Location', related='company_id.liquidation_location_src_id', readonly=False)
    shellon_service_ids = fields.Many2many('product.product', 'shellon_service_rel', string='Shellon Services', related='company_id.shellon_service_ids', readonly=False, domain=[('type', '=', 'service')])
    whole_shrimp_service_ids = fields.Many2many('product.product', 'whole_shrimp_service_rel', string='Whole Shrimp Services', related='company_id.whole_shrimp_service_ids', readonly=False, domain=[('type', '=', 'service')])
    pcd_iqf_service_ids = fields.Many2many('product.product', 'pcd_iqf_service_rel', string='PCD IQF Services', related='company_id.pcd_iqf_service_ids', readonly=False, domain=[('type', '=', 'service')])
    cooked_pyd_service_ids = fields.Many2many('product.product', 'cooked_shrimp_service_rel', string='Cooked PYD IQF Shrimp Services', related='company_id.cooked_pyd_service_ids', readonly=False, domain=[('type', '=', 'service')])
    pyd_block_service_ids = fields.Many2many('product.product', 'pyd_block_service_rel', string='PYD Block Services', related='company_id.pyd_block_service_ids', readonly=False, domain=[('type', '=', 'service')])
class ResCompany(models.Model):
    _inherit = 'res.company'

    liquidation_location_src_id = fields.Many2one('stock.location', 'Source Location')
    shellon_service_ids = fields.Many2many('product.product', 'shellon_service_rel', string='Shellon Services', domain=[('type', '=', 'service')])
    whole_shrimp_service_ids = fields.Many2many('product.product', 'whole_shrimp_service_rel', string='Whole Shrimp Services', domain=[('type', '=', 'service')])
    pcd_iqf_service_ids = fields.Many2many('product.product', 'pcd_iqf_service_rel', string='PCD IQF Services', domain=[('type', '=', 'service')])
    cooked_pyd_service_ids = fields.Many2many('product.product', 'cooked_shrimp_service_rel', string='Cooked PYD IQF Shrimp Services', domain=[('type', '=', 'service')])
    pyd_block_service_ids = fields.Many2many('product.product', 'pyd_block_service_rel', string='PYD Block Services', domain=[('type', '=', 'service')])



