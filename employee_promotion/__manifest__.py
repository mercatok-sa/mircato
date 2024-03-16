# -*- coding: utf-8 -*-
{
    'name': "Employee Promotion",

    'summary': """This app manage employee Promotion 
       """,
    'description': """
        This app manage employee Promotion 
    """,
    'author': "Archer Solutions",
    'website': "www.archersolutions.com",
    'sequence': 1,
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'mail', 'hr_contract'],

    'data': [
        'security/ir.model.access.csv',
        'views/promotion.xml',
        'views/employee.xml',
        'views/mail.xml',

    ],
}
