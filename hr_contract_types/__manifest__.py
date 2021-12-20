# -*- coding: utf-8 -*-

{
    'name': 'Employee Contracts Types',
    'version': '14.0.1.0.0',
    'category': 'Human Resources',
    'summary': """
        Contract type in contracts
    """,
    'description': """ Employee Contracts Types""",
    'author': 'ُEra Group',
    'company': 'Era Group',
    'website': "https://era.net.sa",
    'depends': ['hr', 'hr_contract','hr_payroll'],
    # 'demo': ['data/hr_payroll_demo.xml'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_insurance_security.xml',
        # 'data/hr_contract_type_data.xml',
        'data/hr_payroll_demo.xml',
        'views/contract_view.xml',
        'views/employee_insurance_view.xml',
        'views/insurance_salary_stucture.xml',
        'views/payslip_insurance_view.xml',
        'views/policy_management.xml',

    ],


    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',

}
