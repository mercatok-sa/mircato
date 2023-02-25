# -*- coding: utf-8 -*-
{
    'name': "POS Items Count",
    'summary': 'This app helps you show total items in POS Cart and Pos receipt.',
    'description': """
        Allows the seller to keep track of the total number of items in the POS Cart 
        and POS Receipt. 
    """,
    'author': "Cabrel Tchomte",
    'price': 15,
    'currency': 'USD',
    'license': 'OPL-1',
    'category': 'Point Of Sale',
    'version': '13.0.1.1.0',
    'depends': ['point_of_sale'],
    'data': [
        'views/templates.xml',
    ],
    'images': ['static/description/items_mainscreen.png', 'static/description/items_receipt.png'],
    'qweb': [
         "static/src/xml/*.xml",
    ],
    'installable': True,
    'auto_install': False,
}
