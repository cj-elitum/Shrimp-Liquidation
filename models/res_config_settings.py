from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Liquidation
    liquidation_location_src_id = fields.Many2one('stock.location', 'Source Location', related='company_id.liquidation_location_src_id', readonly=False)

class ResCompany(models.Model):
    _inherit = 'res.company'

    liquidation_location_src_id = fields.Many2one('stock.location', 'Source Location')



