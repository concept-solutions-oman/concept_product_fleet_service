from odoo import models, fields

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    # This overrides the base field and makes it no longer required
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string="Vehicle",
        required=False,  # <-- This is the important change
        help="Vehicle related to this service."
    )

    driver_id = fields.Many2one(
        'res.partner',
        string="Driver",
        help="Driver responsible for this fleet service."
    )

    move_id = fields.Many2one(
        'account.move',
        string="Source Bill",
        readonly=True,
        index=True,
        ondelete='set null',
        help="The vendor bill this service was created from."
    )
    
    # --- NEW FIELD TO DISPLAY ON BUTTON ---
    move_name = fields.Char(
        string="Bill Reference",
        related='move_id.name',
        readonly=True
    )
    # --- END OF NEW FIELD ---

    def action_open_source_bill(self):
        """Open the source vendor bill from the fleet service log."""
        self.ensure_one()
        if not self.move_id:
            return
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bill',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.move_id.id,
            'target': 'current',
        }