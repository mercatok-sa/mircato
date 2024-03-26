# -*- coding: utf-8 -*-
{
    'name': "PriceList Approvals",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Omnya Rashwan",
    'category': 'Product',
    'depends': ['product', 'sale', 'point_of_sale'],
    'data': [
        'security/security.xml',
        'views/pricelist_inh_view.xml',
    ],
}
