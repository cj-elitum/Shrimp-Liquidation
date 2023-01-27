from odoo import models, fields, api


class PackageCategory(models.Model):
    _name = 'shrimp_liquidation.package_category'
    _description = 'Package Category'

    name = fields.Char(string='Name')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name already exists!"),
    ]

