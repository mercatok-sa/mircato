# coding: utf-8
from odoo import models, fields, api, _


class HrTerminationRules(models.Model):
    _name = 'hr.termination.rules'

    termination_config_id = fields.Many2one('hr.config.rules', string="Termination Rule", ondelete='cascade')
    termination_rang_start = fields.Float(string="Range Start(Years)")
    termination_rang_end = fields.Float(string="Range End(Years)")
    termination_days_per_year = fields.Float(string="Days Per Year")
    deduction_amount = fields.Float(string="Amount")
