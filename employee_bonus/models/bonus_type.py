from odoo import fields, models, api, _


class BonusType(models.Model):
    _name = 'bonus.type'

    name = fields.Char(string='Bonus Name')
    type = fields.Selection(selection=[('hour', 'Hour'), ('day', 'Day'), ('fixed', 'Amount')])
