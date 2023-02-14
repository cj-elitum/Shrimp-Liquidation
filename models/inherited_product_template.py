from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    process_type = fields.Selection([
        ('shell_on', 'Shell On'),
        ('pcd_iqf', 'PCD IQF'),
        ('cooked_pyd', 'Cocido PYD IQF'),
        ('pyd_block', 'PYD BLOQUE'),
        ('fresh', 'FRESCOS'),
    ], string="Tipo de proceso")




