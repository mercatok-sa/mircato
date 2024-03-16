# -*- coding: utf-8 -*-
{
    "name": "Employee Bonus",
    "version": "17.0.0.0",
    'category': 'Human Resources',
    'summary': '',
    "description": """""",
    "author": "Eco-Tech, Omnya Rashwan",
    "depends": ['hr', 'hr_contract', 'mercato_contract_enhancement'],
    "data": [
        'security/ir.model.access.csv',
        'views/bonus_type_view.xml',
        'views/employee_bonus_view.xml',
    ],
    "auto_install": False,
    "installable": True,
}
