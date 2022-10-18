# -*- coding: utf-8 -*-
{
    'name': "Petty Cash Extension",

    'summary': """Petty Cash Extension""",

    'description': """Petty Cash Extension
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'petty_cash_management', 'account','hr_expense', 'hr','sale_management'],

    # always loaded
    'data': [
        'security/security_file.xml',
        'security/ir.model.access.csv',
        'views/petty_cash.xml',
        'views/res_user_inh.xml',
        'wizard/sale_config.xml',
        'wizard/petty_cash_per_employee_wizard_view.xml',
        'report/petty_cash_per_employee_report.xml',
        'views/petty_view_inh.xml',
        'views/account_invoice_view.xml',
        'wizard/petty_pay_wizard_view.xml',
        'wizard/invoice_petty_pay_wizard_view.xml',
        'wizard/petty_cash_transfer_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
