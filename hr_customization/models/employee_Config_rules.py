# coding: utf-8
from odoo import models, fields, api, _
from datetime import datetime


class HrConfigRules(models.Model):
    _name = 'hr.config.rules'

    name = fields.Char(string="Rule Name")
    month_work_days = fields.Integer(string="Month Work Days")
    terminations_rule_ids = fields.One2many('hr.termination.rules', 'termination_config_id', string="Termination Rules")
    resignation_rule_ids = fields.One2many('hr.resignation.rules', 'resignation_config_id', string="Resignation Rules")

    @api.model
    def default_get(self, fields):
        res = super(HrConfigRules, self).default_get(fields)
        term_rules = [
            (0, 0, {'termination_rang_start': 0, 'termination_rang_end': 5, 'termination_days_per_year': 15,
                    'deduction_amount': 1.0}),
            (0, 0, {'termination_rang_start': 5, 'termination_rang_end': 100, 'termination_days_per_year': 30,
                    'deduction_amount': 1.0}),
        ]
        regis_rules = [
            (0, 0, {'resignation_rang_start': 0, 'resignation_rang_end': 3, 'resignation_days_per_year': 0.0,
                    'deduction_amount': 0.0}),
            (0, 0, {'resignation_rang_start': 3, 'resignation_rang_end': 5, 'resignation_days_per_year': 15,
                    'deduction_amount': 0.50}),
            (0, 0, {'resignation_rang_start': 5, 'resignation_rang_end': 10, 'resignation_days_per_year': 30,
                    'deduction_amount': 0.67}),
            (0, 0, {'resignation_rang_start': 10, 'resignation_rang_end': 100, 'resignation_days_per_year': 30,
                    'deduction_amount': 1}),
        ]
        res['terminations_rule_ids'] = term_rules
        res['resignation_rule_ids'] = regis_rules
        return res
