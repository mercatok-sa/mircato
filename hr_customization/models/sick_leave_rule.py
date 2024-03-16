# coding: utf-8
from odoo import models, fields, api, _


class SickLeaveRules(models.Model):
    _name = 'sick.leave.rule'

    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")
    name = fields.Char(string="Rule Name")
    days_from = fields.Float(string="Days From")
    days_to = fields.Float(string="Days To")
    deduction = fields.Float(string="Deduction")
