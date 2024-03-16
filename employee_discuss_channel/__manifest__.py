# -*- coding: utf-8 -*-
{
    'name': "HR Discuss Channel",
    'category': 'hr',
    'summary': 'HR Discuss Channel',
    'description': """HR Discuss Channel""",

    'author': "Archer Solutions",
    'website': "www.archersolutions.com",
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': [
        'mail',
        'hr',
    ],
    # always loaded
    'data': [

        'data/mail_channel_hr_data.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
