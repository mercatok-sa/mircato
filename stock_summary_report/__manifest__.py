# -*- coding: utf-8 -*-
{
    'name': "Stock Summary Report",

    'summary': """
        Get the Overall Stock Summary of Location Between Two Dates.""",

    'description': """
        Get the Overall Stock Summary with Transaction Between Two Dates.
        
    """,

    'author': "10 Orbits",
    'website': "https://www.10orbits.com/",
    'category': 'Warehouse',
    'version': '0.1',
    'depends': ['base','report_xlsx','stock'],
    'data': [
        'wizard/stock_summary.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
