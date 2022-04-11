 # -*- coding: utf-8 -*-
{
    'name': "Nati Reports Header and footer",

    'summary': """
        Redesign of Header and footer, keeping the official and modern look """,

    'description': """
Many modern designs and shapes, with additional features, 
for example: line numbers, numbers in words, compatibility with different printing options,
english and arabic lable,for both LTR and RTL
    """,
    'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'license': 'AGPL-3',
    'category': 'Extra Tools',
    'version': '15.0.0.0',
    'depends': ['base','web'],
    'qweb': [],
    'data': ['views/res_company.xml',
             'views/base_document_layout.xml',
             'views/report_templates.xml',
             'data/report_layout.xml',
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'live_test_url': 'https://youtu.be/FBInHHij18Q',

}

