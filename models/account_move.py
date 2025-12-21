from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    has_fleet_product = fields.Boolean(
        string="Has Fleet Product",
        compute="_compute_has_fleet_product",
        store=True
    )

    analytic_distribution = fields.Json(
        string="Analytic Distribution",
        help="Analytic accounts and percentages related to this bill."
    )

    analytic_precision = fields.Integer(
        string="Analytic Precision",
        compute="_compute_analytic_precision",
        store=False
    )

    service_type_id = fields.Many2one(
        'fleet.service.type',
        string="Service Type",
        help="Select the fleet service type related to this product."
    )

    # --- NEW FIELDS ---
    service_log_ids = fields.One2many(
        'fleet.vehicle.log.services',
        'move_id',
        string="Fleet Services"
    )
    
    service_log_count = fields.Integer(
        string="Fleet Service Count",
        compute="_compute_service_log_count",
        store=True
    )

    # --- NEW COMPUTE METHOD ---
    @api.depends('service_log_ids')
    def _compute_service_log_count(self):
        for move in self:
            move.service_log_count = len(move.service_log_ids)

    @api.depends()
    def _compute_analytic_precision(self):
        """Default analytic precision for analytic widget."""
        for record in self:
            record.analytic_precision = 2

    @api.depends('invoice_line_ids.product_id')
    def _compute_has_fleet_product(self):
        for move in self:
            move.has_fleet_product = any(
                line.product_id.is_fleet for line in move.invoice_line_ids
            )

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id_fetch_analytic(self):
        """When selecting a vehicle, auto-load its analytic distribution."""
        for move in self:
            if move.vehicle_id and move.vehicle_id.analytic_distribution:
                move.analytic_distribution = move.vehicle_id.analytic_distribution
            else:
                move.analytic_distribution = False

    def action_add_fleet_service(self):
        """Create a Fleet Service record for fleet-enabled products (Vendor Bills only)."""
        FleetService = self.env['fleet.vehicle.log.services']
        
        created_service_ids = []

        for move in self:
            if move.move_type != 'in_invoice':
                raise UserError("Fleet Service creation is only allowed for Vendor Bills.")

            for line in move.invoice_line_ids.filtered(lambda l: l.is_fleet):
                product_service_type = line.product_id.service_type_id

                if not product_service_type:
                    raise UserError(
                        f"The product '{line.product_id.display_name}' is marked as a "
                        "fleet cost but does not have a Service Type configured. "
                        "Please update the product in the Inventory tab."
                    )

                analytic_info = ""
                if line.analytic_distribution:
                    parts = []
                    for key, value in line.analytic_distribution.items():
                        analytic_account = self.env['account.analytic.account'].browse(int(key))
                        parts.append(f"[{analytic_account.code or analytic_account.id}] {analytic_account.name} ({value}%)")
                    analytic_info = "\nAnalytic Distribution:\n" + "\n".join(parts)

                # This line checks for a vehicle on the line OR on the main bill
                vehicle = line.vehicle_id or move.vehicle_id
                
                # --- VALIDATION BLOCK HAS BEEN REMOVED ---
                # The "if not vehicle:" check is now gone.

                driver = vehicle.driver_id.id if vehicle and vehicle.driver_id else False

                created_service = FleetService.create({
                    'description': line.name or line.product_id.display_name or 'Fleet Service',
                    'vendor_id': move.partner_id.id,
                    'amount': line.price_subtotal,
                    'date': move.invoice_date or fields.Date.today(),
                    # --- FIX: Allow False if no vehicle is selected ---
                    'vehicle_id': vehicle.id if vehicle else False,
                    'driver_id': driver,
                    'service_type_id': product_service_type.id,
                    'move_id': move.id,
                    'notes': (
                        f"{move.name or ''}.\n"
                        f"{analytic_info if analytic_info else ''}"
                    ),
                })
                created_service_ids.append(created_service.id)

        if created_service_ids:
            self._compute_service_log_count()
            return self.action_show_fleet_services()
        else:
            raise UserError("No fleet-enabled products found in this bill.")

    # --- NEW ACTION METHOD ---
    def action_show_fleet_services(self):
        """Show the fleet service logs linked to this bill."""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('fleet.fleet_vehicle_log_services_action')
        
        if self.service_log_count > 1:
            action['domain'] = [('id', 'in', self.service_log_ids.ids)]
        else:
            action['views'] = [(self.env.ref('fleet.fleet_vehicle_log_services_view_form').id, 'form')]
            action['res_id'] = self.service_log_ids.id
        
        action['target'] = 'current'
        return action