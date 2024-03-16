# -*- coding: utf-8 -*-
{
    'name': "Contract Printout",

    'summary': """
        This Module add new template for contract.
        """,

    'author': "Omnya Rashwan",
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract', 'hr'],

    # always loaded
    'data': [
        'reports/contract_template_report.xml',
    ],
}
