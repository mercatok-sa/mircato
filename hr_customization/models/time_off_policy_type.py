# coding: utf-8
from odoo import models, fields, api, _


class TimeOffPolicyType(models.Model):
    _name = 'time.off.policy.type'
    _rec_name = "time_off_id"

    time_off_policy_type_id = fields.Many2one('time.off.policy', string="Type")
    time_off_id = fields.Many2one('hr.leave.type', string="Type")
