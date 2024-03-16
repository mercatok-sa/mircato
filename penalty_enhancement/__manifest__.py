# -*- coding: utf-8 -*-
{
    'name': "Penalty Enhancement",
    'author': "Eco-Tech, Omnya Rashwan",
    'category': 'Penalties',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'penalty_request'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/penalty_email_template.xml',
        'views/hr_employee_inh_view.xml',
        'views/penalty_rule_view.xml',
        'views/penalty_request_inh_view.xml',
        'reports/penalty_request_template.xml',
    ],
}
