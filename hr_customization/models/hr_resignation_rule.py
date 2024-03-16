# coding: utf-8
from odoo import models, fields, api, _


class HrResignationRules(models.Model):
    _name = 'hr.resignation.rules'

    resignation_config_id = fields.Many2one('hr.config.rules', string="Resignation Rule", ondelete='cascade')
    resignation_rang_start = fields.Float(string="Range Start(Years)")
    resignation_rang_end = fields.Float(string="Range End(Years)")
    resignation_days_per_year = fields.Float(string="Days Per Year")
    deduction_amount = fields.Float(string="Amount")
