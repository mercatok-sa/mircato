# See LICENSE file for full copyright and licensing details

{
    # Module Information
    'name': 'Employee Portal Time Off',
    'category': 'Website',
    'version': '17.0.0.1.0',
    'summary': 'Portal user can manage leaves from Website Portal',
    'description': """Portal user can manage leaves from Website Portal""",
    # Dependencies
    'depends': [
        'base',
        'website',
        'portal',
        'hr_enhancement', 'custom_portal_account_page'
    ],
    # Views
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            "employee_portal_timeoff/static/src/js/leave_portal.js",
            "employee_portal_timeoff/static/src/js/portal_timeoff.js",
            "employee_portal_timeoff/static/src/scss/custom_style.scss"
        ]
    },
    # Author
    'author': 'Techinsider Solution',
    'images': ['static/description/emp_timeoff_poster_offer.png'],
    'installable': True,
}
