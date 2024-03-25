# -*- coding: utf-8 -*-
{
    'name': "Accounting Enhancement",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Omnya Rashwan",
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'security/security_group.xml',
        'views/account_move_inh_view.xml',
    ],
}
