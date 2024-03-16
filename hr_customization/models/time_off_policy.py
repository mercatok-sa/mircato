# coding: utf-8
from odoo import models, fields, api, _


class TimeOffPolicy(models.Model):
    _name = 'time.off.policy'
    _rec_name = "name"

    name = fields.Char(string="Name")
    line_ids = fields.One2many('time.off.policy.type', 'time_off_policy_type_id', string="Lines")
