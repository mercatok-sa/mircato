# -*- coding: utf-8 -*-
{
    'name': "Po Access Right",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Omnya Rashwan",
    'category': 'Purchasing',
    'depends': ['purchase'],
    'data': [
        'security/security_group.xml',
        'views/po_inh_view.xml',
    ],
}
