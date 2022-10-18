# -*- coding: utf-8 -*-
{
    'name': "Sale Order analytic Account",
    'license': 'OPL-1',
    'summary': """
        Automatic creation for sale analytic account""",

    'description': """
        This module will create analytic account automatically once sale is confirmed, 
        new created analytic account will be assigned to analytic account field in SO.
        analytic account.
        create automatic analytic account
        sales analytic account
        sale analytic account
        analytic
        automatic creation for analytic account
        analytic account creation
    """,

    'author': 'CorTex IT Solutions Ltd.',
    'website': 'https://cortexsolutions.net',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '15.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_management','analytic'],
    'installable': True,
    'auto_install': False,
    # always loaded
    'data': [
    ],
}
