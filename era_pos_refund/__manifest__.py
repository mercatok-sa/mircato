# -*- coding: utf-8 -*-
{
    'name' : 'ERA POS Refund',
    'version' : '15.0.0.1',
    'summary': 'ERA POS Refund',
    'description': """ Show all orders in refund from any POS in addition to a new security group for the refund process""",
    'category': 'Sales/Point of Sale',
    'auther': 'ERA Group',
    'email': 'info@era.net.sa',
    'website': 'https://era.net.sa',
    'depends' : ['point_of_sale'],
    'data': [
        'security/pos_security.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'point_of_sale.assets': [
            'era_pos_refund/static/src/css/pos.css',
            'era_pos_refund/static/src/js/models.js',
            'era_pos_refund/static/src/js/refundbutton.js',
        ],
        'web.assets_qweb': [
            'era_pos_refund/static/src/xml/**/*',
        ],
    }
}
