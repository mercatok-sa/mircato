from odoo import fields, models, api, _


class ContractProbationPeriod(models.Model):
    _name = 'contract.probation.period'

    name = fields.Char(string='Probation Period', required=True)
