# -*- coding: utf-8 -*-
{
    'name': "ERA POS Invoice",
    "version" : "15.0.0.3",
    "category" : "Accounting",
    'description': """
        ERA POS Invoice
    """,
    'author': "Era group",
    'email': "aqlan@era.net.sa ",
    'website': "https://era.net.sa",
    'category': 'accounting',
    'price': 0,  
    'currency': 'USD',
    'version': '0.1',
    'license': 'AGPL-3',
    'images': ['static/description/main_screenshot.png'],
    # 'depends': ['base', 'account', 'point_of_sale', 'era_pos_tax_invoice'],
    'depends': ['base', 'account', 'point_of_sale'],
    "data": [
        'report/pos_report.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    "application": True,

    'assets': {
        'web.assets_qweb': [
            'era_pos_invoice/static/src/xml/era_l10n_sa_pos.xml',
        ],
    },


}
