# -*- coding: utf-8 -*-
{
    'name': 'ERA Pos Item count',
    'version': '15.0.2.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'auther': 'ERA Group',
    'email': 'info@era.net.sa',
    'website': 'https://era.net.sa',
    'summary': 'Pos Item count module show you number of products in cart.',
    'description': """ This module show you number of products in cart.""",
    'depends': ['point_of_sale', 'base'],
    'data': [
        'views/res_users_view.xml',
    ],
    'images': [
    ],
    'assets': {
            'point_of_sale.assets': [
                'era_pos_item_count/static/src/**/*',
            ],
            'web.assets_qweb': [
                'era_pos_item_count/static/src/**/*',
            ],
        },

    'installable': True,
    'auto_install': False,

}

