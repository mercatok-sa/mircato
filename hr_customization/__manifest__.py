# -*- coding: utf-8 -*-
{
    'name': "Hr Customization",
    'summary': """""",
    'description': """""",
    'category': 'hr',
    'version': '1.0.0',
    'depends': ['base', 'hr', 'hr_holidays', 'hr_payroll', 'account_accountant', 'rm_hr_attendance_sheet',
                # 'custom_portal_account_page'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_config_rules_view.xml',
        'views/hr_termination_request.xml',
        'views/hr_resignation_request.xml',
        'views/hr_leave_type_inherit.xml',
        'views/hr_employee_inherit.xml',
        'views/employee_leaves_report.xml',
        'views/hr_leave_request_inherit.xml',
        'views/hr_payslip_view.xml',
        'views/hr_payslip_run_view.xml',
        'views/check_employee_expiry_date_report.xml',
        'views/employee_check_list_view.xml',
        'views/employee_document_view.xml',
        'views/hr_contract_views.xml',
        'views/end_of_service_recognition.xml',
        # 'views/res_config_setting.xml',
        'views/time_off_policy_view.xml',
        'views/menus.xml',
        'wizard/payslip_mass_mailing.xml',
        'wizard/check_employee_leaves.xml',
        'wizard/check_document_expiry_date.xml',
        'data/annual_leave_schedule_action.xml',
        'data/payslip_mail_template.xml',
        'data/payslip_emailtemplate.xml',
        # 'views/templates.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            "hr_customization/static/src/js/reg_portal.js",
            "hr_customization/static/src/js/registration_portal.js",
        ]
    },
}
