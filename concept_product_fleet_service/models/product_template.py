from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_fleet = fields.Boolean(
        string="Cost Fleet",
        help="Enable if this product is used for fleet management."
    )

    service_type_id = fields.Many2one(
        'fleet.service.type',
        string="Service Type",
        help="Select the fleet service type related to this product."
    )

