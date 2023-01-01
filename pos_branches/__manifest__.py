# -*- coding: utf-8 -*-
{
    'name': "POS Branches",
    "version": "15.0.0.1",
    "category": "Accounting",
    'description': """
        POS Branches
    """,
    'author': "Nasreldin Omar",
    'email': "nasrom9@gmail.com",
    'version': '0.1',
    'license': 'AGPL-3',
    'images': [],
    'depends': ['point_of_sale'],
    "data": [
        'security/ir.model.access.csv',
        'views/pos_branch_view.xml',
        'views/pos_views.xml',
        # 'report/action_pos_report.xml',
        # 'wizard/pos_details_wizard.xml',
    ],
    'qweb': [],
    "application": True,

}
