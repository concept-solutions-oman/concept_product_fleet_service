{
    'name': 'Batch Payment',
    'version': '17.0.0.0.0',
    'category': 'Purchases',
    'summary': 'Adds Is Fleet checkbox in Product Purchase tab.',
    'description': """
        Fleet Service Auto Creation from Vendor Bills - Odoo 17
        =======================================================
        
        This module streamlines the Fleet Management workflow by linking
        products to fleet services and automatically creating service records
        from vendor bills.

        Key Features:
        1. Fleet Configuration:
           - Each Fleet Service type can be linked to a product from the Inventory.

        2. Vendor Bill Integration:
           - When a vendor bill line includes a configured product,
             a "Create Fleet Service" button will appear.
           - Clicking the button auto-generates a Fleet Service record in Draft state.

        3. Auto Data Transfer:
           The following details are automatically filled into the Fleet Service:
           - Vehicle (mandatory selection)
           - Service product and cost
           - Vendor details
           - Description / Reference
           - Bill Date as Service Date

        4. Vehicle Auto-Suggestion:
           - If an Analytic Account is selected on the bill and linked to a vehicle,
             the system will auto-select that vehicle.
           - After saving, the Analytic Account value is retained.

        Benefit:
        Eliminates manual efforts, reduces data entry errors, and ensures
        accurate linkage between vendor expenses and fleet service operations.
    """,

    'author': 'Concept Solutions',
    'website': 'https://www.csloman.com',
    'license': 'LGPL-3',
    'depends': [
        'product', 'purchase', 'account', 'fleet'
    ],
    'data': [
        'views/account_move_views.xml',
        'views/fleet_vehicle_inherit_view.xml',
        'views/product_template_views.xml',
        'views/fleet_vehicle_log_services_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 360.00,
    'currency': 'USD',
}