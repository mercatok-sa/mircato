# -*- coding: utf-8 -*-
{
    'name': 'QERP Whatsapp POS',
    'version': '15.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'author': 'Mohamed Rabiea',
    'website': 'http://www.qualityerp.com',
    'depends': ['point_of_sale', 'sale_management', 'tus_meta_whatsapp_base', 'tus_meta_wa_pos'],
    'data': [
        'views/pos_order_portal_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_frontend': [
        ],
        'point_of_sale.assets': [
            '/qerp_whatsapp_pos/static/src/js/ClientDetailsEdit.js',
            '/qerp_whatsapp_pos/static/src/js/ProductScreen.js',
        ],
    }
}
