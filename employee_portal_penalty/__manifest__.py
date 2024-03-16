# See LICENSE file for full copyright and licensing details

{
    'name': 'Employee Portal Penalties',
    'category': 'Website',
    'version': '1.0',
    'summary': 'Portal user can manage penalties from Website Portal',
    'description': """
        Portal user can manage penalties from Website Portal
    """,
    # Dependencies
    'depends': ['base', 'hr',
                'website', 'portal', 'hr_enhancement', 'penalty_request', 'penalty_enhancement'
                ],
    # Views
    'data': [
        'views/penalty_portal_templates.xml',
    ],
    "assets": {
        "web.assets_frontend": [
            # "employee_portal_penalty/static/src/js/penalty_portal.js",
            "employee_portal_penalty/static/src/js/penalty_edit.js",
        ]
    },
    # Author
    'author': 'Omnya Rashwan',
    'installable': True,
}
