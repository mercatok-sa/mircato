# -*- coding: utf-8 -*-
{
    'name': "TeleNoc E-Invoice KSA - POS | QR Code | POS | ZATCA | VAT | E-Invoice | Tax | Zakat",
    'summary': 'TeleNoc E-Invoice for POS is fully compatible with Odoo standard invoice template.',
    'version': '15.0.1.0.0',
    "category" : "Accounting",
    'description': """
        Electronic invoice KSA - POS
    """,
    'author': 'Odoo Team, Telenoc',
    'email': "info@telenoc.org",
    'website': "https://telenoc.org",
    'category': 'accounting',
    'license': 'AGPL-3',
    'images': ['static/description/banner.jpg',
              'static/description/apps_screenshot.jpg'],
    'depends': ['base', 'account', 'point_of_sale',],
    "data": [],
    'qweb': ['static/src/xml/pos.xml'],
    "application": True,
    'assets': {
        'point_of_sale.assets': [
            'telenoc_pos_sa_invoice/static/src/js/qrcode.js',
            'telenoc_pos_sa_invoice/static/src/js/pos.js',
        ],
        'web.assets_qweb': [
            'telenoc_pos_sa_invoice/static/src/xml/**/*',
        ],
    },
}
