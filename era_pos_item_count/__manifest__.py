# -*- coding: utf-8 -*-
{
    'name': 'ERA Pos Item count',
    'version': '15.0.1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'auther': 'ERA Group',
    'email': 'info@era.net.sa',
    'website': 'https://era.net.sa',
    'summary': 'Pos Item count module show you number of products in cart.',
    'description': """ This module show you number of products in cart.""",
    'depends': ['point_of_sale', 'base'],
    'data': [
        # 'security/pos_security.xml',
    ],
    'images': [
    ],
    'assets': {
        'web.assets_qweb': [
            'era_pos_item_count/static/src/xml/pos.xml',
            'era_pos_item_count/static/src/xml/ClosePosPopup.xml',
        ],
        'point_of_sale.assets': [
            'era_pos_item_count/static/src/js/pos.js',
        ]
    },

    'installable': True,
    'auto_install': False,

}

