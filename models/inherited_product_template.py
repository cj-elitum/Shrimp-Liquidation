from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    size = fields.Char(string="Tamaño")


