# -*- coding: utf-8 -*-

# Copyright © 2018-2020 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

{
    'name': 'Restriction of POS User',
    'version': '15.0.1.0.0',
    'category': 'Point of Sale',
    'author': 'Garazd Creation',
    'website': 'https://garazd.biz',
    'license': 'LGPL-3',
    'summary': 'Restrict POS Users to allowed Points of Sale.',
    'images': ['static/description/banner.png'],
    'description': """
The module allows restricting access to Points of Sale for POS users.
    """,
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'security/pos_user_restrict_security.xml',
        'views/res_users_views.xml',
    ],
    'external_dependencies': {
    },
    'support': 'support@garazd.biz',
    'application': False,
    'installable': True,
    'auto_install': False,
}
