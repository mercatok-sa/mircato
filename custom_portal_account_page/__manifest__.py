# -*- coding: utf-8 -*-
{
    'name': "MyAccount Portal Page Layout",

    'summary': """
        This Module change Portal Account page design with changing profile picture feature.
        """,

    'author': "Amel Salah",
    'website': "https://github.com/amelsalah",

    'category': 'portal',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'hr', 'employee_promotion', 'rm_hr_attendance_sheet', 'website'],

    # always loaded
    'data': [

        'views/templates.xml',
        'views/payslip_template.xml',
        'views/promotion_template.xml',
        'views/attendance_template.xml',

    ],
    'images': [
        'static/description/screenshot.png',

    ],

}
