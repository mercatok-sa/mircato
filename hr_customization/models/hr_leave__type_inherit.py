# coding: utf-8
from odoo import models, fields, api, _


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    annual_leave = fields.Boolean(string="Annual Leave")
    pay_in_advance = fields.Boolean(string="Allow Pay in Advance")
    sick_leave = fields.Boolean(string="Sick Leave")
    calculate_in_ter_resi = fields.Boolean(string='Cal. in Termination and Resignation')

    sick_leave_rules_ids = fields.One2many('sick.leave.rule', 'leave_type_id', string="Sick Leave Rules")
    is_unpiad_leave = fields.Boolean(string="Is Unpaid Leave", )
