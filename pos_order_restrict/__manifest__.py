# -*- coding: utf-8 -*-

{
    'name': 'POS Order Restrict',
    'summary': """Restricts User access to pos and orders""",
    'version': '15.0.1.0.0',
    'description': """Restricts User access to pos and orders""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://cybrosys.com',
    'category': 'Tools',
    'depends': ['base','point_of_sale','pos_restrict'],
    'license': 'AGPL-3',
    'data': [
        'security/security.xml',
        'views/pos_order_menu.xml'
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
