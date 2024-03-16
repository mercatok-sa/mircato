# -- coding: utf-8 --
{
    'name': 'Open HRMS Overtime',
    'version': '17.0.1.0.0',
    'summary': 'Manage Employee Overtime',
    'description': """ Helps you to manage Employee Overtime.""",
    'category': 'Generic Modules/Human Resources',
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'website': "https://www.openhrms.com",
    'depends': [
        'hr', 'hr_contract', 'hr_attendance', 'hr_holidays', 'project', 'hr_payroll', 'dev_hr_loan'
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'data': [

        'data/data.xml',
        'views/overtime_request_view.xml',
        'views/overtime_type.xml',
        'views/hr_contract.xml',
        # 'views/hr_payslip.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['data/hr_overtime_demo.xml'],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
