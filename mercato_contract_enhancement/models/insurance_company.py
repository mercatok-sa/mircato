from odoo import fields, models, api, _


class InsuranceCompany(models.Model):
    _name = 'insurance.company'

    name = fields.Char('Insurance Company Name')
