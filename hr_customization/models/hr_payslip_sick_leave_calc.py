# coding: utf-8
from odoo import models, fields, api, _
import datetime


class HrPayslipSIckLeaveCalc(models.Model):
    _name = 'hr.payslip.sick.leave.calc'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee')
    number_of_days = fields.Float()
    is_payslip_computed = fields.Boolean()
