from odoo import fields, models, api, _


class PenaltyRle(models.Model):
    _name = 'penalty.rule'

    name = fields.Char(string='name', required=True)
    number_of_days = fields.Integer()
    penalty_type = fields.Selection(selection=[('amount', 'Amount'), ('days', 'Days')], required=True)
    line_ids = fields.One2many(comodel_name='hr.penalty.rule',
                               inverse_name='penalty_id',
                               string='Penalty In Periods')


class HrPenaltyRule(models.Model):
    _name = 'hr.penalty.rule'

    penalty_id = fields.Many2one(comodel_name='penalty.rule')
    rate = fields.Float(string='Rate', required=True)
    counter = fields.Selection(string="Times", selection=[
        ('1', 'First Time'),
        ('2', 'Second Time'),
        ('3', 'Third Time'),
        ('4', 'Fourth Time'),
        ('5', 'Fifth Time')], required=True)
