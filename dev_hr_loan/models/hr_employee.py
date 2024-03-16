# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    loan_request = fields.Integer(string='Loan Request Per Year', default=1, required=True, help="Loan Request",
                                  store=True)


class HrEmployeesPublic(models.Model):
    _inherit = 'hr.employee.public'

    loan_request = fields.Integer(string='Loan Request Per Year')
