from odoo import models, fields, api


class LiquidationPackage(models.Model):
    _name = 'shrimp_liquidation.liquidation.package'
    _description = 'Package'

    name = fields.Char(string="Empaque")
    pounds_per_package = fields.Float(string="Libras por empaque")

