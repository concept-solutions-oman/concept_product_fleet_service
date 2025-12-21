from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_fleet = fields.Boolean(
        string="Cost Fleet",
        compute="_compute_is_fleet",
        store=True,
        readonly=True,
        help="Indicates whether this line is related to a fleet service."
    )

    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string="Vehicle",
        help="Select the vehicle this bill line belongs to."
    )

    @api.depends('product_id', 'product_id.is_fleet')
    def _compute_is_fleet(self):
        for line in self:
            line.is_fleet = bool(line.product_id and line.product_id.is_fleet)

    # --------------------------------------------------------------------------
    # AUTO-FETCH ANALYTIC WHEN VEHICLE IS SELECTED
    # --------------------------------------------------------------------------
    @api.onchange('vehicle_id')
    def _onchange_vehicle_id_fetch_analytic(self):
        """Auto-fetch analytic distribution from selected vehicle."""
        for line in self:
            # FIX: Only update if the vehicle explicitly has a distribution.
            # We REMOVED the 'else' block so it does not clear your manual entry
            # if the vehicle has no default distribution.
            if line.vehicle_id and line.vehicle_id.analytic_distribution:
                line.analytic_distribution = line.vehicle_id.analytic_distribution

    # --------------------------------------------------------------------------
    # AUTO-FETCH VEHICLE WHEN ANALYTIC IS SELECTED
    # --------------------------------------------------------------------------
    @api.onchange('analytic_distribution')
    def _onchange_analytic_distribution_set_vehicle(self):
        """Auto-select vehicle based on analytic account code."""
        for line in self:
            if line.is_fleet and line.analytic_distribution:
                # Get the first analytic account ID from the dictionary keys
                analytic_ids = list(line.analytic_distribution.keys())
                if analytic_ids:
                    # Convert key to int as JSON keys are strings
                    analytic_account_id = int(analytic_ids[0])
                    analytic_account = self.env['account.analytic.account'].browse(analytic_account_id)
                    
                    if analytic_account and analytic_account.code:
                        # Search for a vehicle with a matching license plate
                        vehicle = self.env['fleet.vehicle'].search(
                            [('license_plate', '=', analytic_account.code)],
                            limit=1
                        )
                        if vehicle:
                            line.vehicle_id = vehicle