# -*- coding: utf-8 -*-
{
    'name': "Electronic invoice KSA - Sales & Purchase",
    'description': """
       Electronic invoice KSA - Sales & Purchase
    """,
    'author': "Era group",
    'email': "aqlan@era.net.sa ",
    'website': "https://era.net.sa",
    'category': 'accounting',
    'version': '0.1',
    'price': 294,  
    'currency': 'USD',
    'license': 'AGPL-3',
    'images': ['static/description/main_screenshot.png'],
    'depends': ['base', 'account', 'sale', 'purchase'],
    'data': [
        'views/partner.xml',
        'reports/invoice_inherit_report.xml',
    ],
}
