# -*- coding: utf-8 -*-
{
    'name': "Geidea Terminal Integration",

    'summary': """
        This module provides integration between, Odoo POS Module and Saudi Arabian Geidea POS Terminal without the need to use POSBox.  
    """,

    'description': """
        This module provides integration between, Odoo POS Module and Saudi Arabian Geidea POS Terminal without the need to use POSBox.
        NOTE:
            - We only support odoo running on linux environment, we DO NOT SUPPORT WINDOWS
            - Cashier workstation MUST be windows only, not android not ios
            - The module only supports USB 
            - We are collecting telemetry data to ensure best support and make sure our module is working as expected without issues, by purchasing this module you agree to allow us collect such data.
            Data we collect is not related to your personal or customer's personal data. we collect VAT number, odoo version, data about transaction limited to amount, and datetime, data we collect are subject to change and description will be updated.
    """,

    'author': "Barameg",
    'website': "https://barameg.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '15.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],
    'images': [
        'static/src/img/cover.png',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/pos_payment_method.xml',
        'views/pos_order.xml',
        'views/pos_payment.xml',
        'views/geidea_terminals.xml',
        'actions/geidea_terminals.xml',
        'actions/geidea_terminals.xml',
    ],
    'assets': {
        'web.assets_tests': [
            # 'point_of_sale/static/tests/tours/**/*',
        ],
        'point_of_sale.assets': [
            'barameg_geidea_pos/static/src/js/models.js',
            'barameg_geidea_pos/static/src/js/screens.js',
        ],
        'web.assets_backend': [
        ],
        'point_of_sale.pos_assets_backend': [
            # ('include', 'web.assets_backend'),
            # ('remove', 'web/static/src/webclient/menus/menu_service.js'),
            # ('remove', 'web/static/src/core/errors/error_handlers.js'),
            # ('remove', 'web/static/src/legacy/legacy_rpc_error_handler.js'),
        ],
        'point_of_sale.pos_assets_backend_style': [
            # "web/static/src/core/ui/**/*.scss",
        ],
        'point_of_sale.tests_assets': [
        ],
        'point_of_sale.qunit_suite_tests': [
            # 'web/static/tests/legacy/component_extension_tests.js',
            # 'point_of_sale/static/tests/unit/**/*',
        ],
        'point_of_sale.assets_backend_prod_only': [
            # 'point_of_sale/static/src/js/chrome_adapter.js',
            # 'point_of_sale/static/src/js/main.js',
            # 'web/static/src/start.js',
            # 'web/static/src/legacy/legacy_setup.js',
        ],
        'web.assets_qweb': [
            # 'point_of_sale/static/src/xml/**/*',
        ],
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'price': 500.00,
    'currency': 'EUR',

}
