# -*- coding: utf-8 -*-
{
    'name': "Leaves Printout",

    'summary': """
        This Module add new template for leaves request.
        """,

    'author': "Omnya Rashwan",
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_holidays', 'hr'],

    # always loaded
    'data': [
        'views/hr_leave_inh_view.xml',
        'reports/leave_template_report.xml',
    ],
}
