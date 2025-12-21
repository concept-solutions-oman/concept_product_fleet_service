from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    analytic_distribution = fields.Json(
        string="Analytic Distribution",
        help="Define the analytic account split for this vehicle."
    )

    analytic_precision = fields.Integer(
        string="Analytic Precision",
        compute="_compute_analytic_precision",
        store=False
    )

    @api.depends()
    def _compute_analytic_precision(self):
        """Default analytic precision, same as accounting (2 decimals)."""
        for record in self:
            record.analytic_precision = 2
