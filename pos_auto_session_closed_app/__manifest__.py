# -*- coding: utf-8 -*-
{
    "name" : "POS Session Auto Validate Odoo",
    "author": "Edge Technologies",
    "version" : "15.0.1.0",
    "live_test_url":'https://youtu.be/v3_tf8Fmpzc',
    "images":['static/description/main_screenshot.png'],
    'summary': 'Apps for Auto Validate pos Session automatic Validate pos Session automatic close pos session close automatic pos session validate automatic point of sale validate auto point of sale session validate automatic session close ',
    "description": """
        This moudle helps to Auto Validate and Closed Pos Session thorugh Scheduler.
    """,
    "license" : "OPL-1",
    "depends" : ['base','point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/pos_session_cron.xml',
        'views/pos_seesion_close.xml',        
    ],

    'qweb' : [],
    "auto_install": False,
    "installable": True,
    "price": 39,
    "currency": 'EUR',
    "category" : "Point of Sale",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
