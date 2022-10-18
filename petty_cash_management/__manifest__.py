# -*- coding: utf-8 -*-
{
    'name': "Petty Cash Management",

    'summary': """
        Petty Cash Management""",

    'description': """
        Petty Cash Management
    """,

    'author': "IMCC",
    'website': "http://www.imcc.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'account',
    'version': '1.1',

    # any module necessary for this one to work correctly
    # 'depends': ['base','branch', 'account','hr','hr_expense'],
    'depends': ['base','base_automation', 'account','hr',
    #'account_budget',
    'hr_expense'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/petty_cash_data.xml',
        'data/template.xml',
        'views/payment_view.xml',
        'views/petty_cash_type_view.xml',
        'views/petty_view.xml',
        'wizard/petty_pay_wizard_view.xml',
        'views/hr_expense_view.xml',
        'views/account_invoice_view.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
