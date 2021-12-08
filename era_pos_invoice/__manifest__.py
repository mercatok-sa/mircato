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
    # 'depends': ['base', 'account', 'point_of_sale'],
    'depends': ['point_of_sale'],
    "data": [],
    'qweb': ['static/src/xml/pos.xml'],
    "application": True,

    'assets': {
        # 'point_of_sale.assets': [
        #     'era_pos_invoice/static/src/js/pos.js',
        # ],
        'web.assets_qweb': [
            'era_pos_invoice/static/src/xml/pos_new.xml',
        ],
    },


}
