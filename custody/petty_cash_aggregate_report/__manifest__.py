# -*- coding: utf-8 -*-
{
    'name': "petty_cash_aggregate_report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_expense','petty_cash_extention','petty_cash_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_expense_view_inh.xml',
        'views/account_invoice_view.xml',
        'wizard/petty_cash_per_employee_wizard_view.xml',
        'report/petty_cash_per_employee_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
