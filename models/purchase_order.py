from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidación", ondelete='cascade')
    service_liquidation_id = fields.Many2one('shrimp_liquidation.liquidation', string="Liquidación de Servicio", ondelete='cascade')
