from odoo import fields, models, api, _


class EmployeeBonus(models.Model):
    _name = 'employee.bonus'

    name = fields.Char()
    bonus_type = fields.Many2one(comodel_name='bonus.type')
    date = fields.Date()
    value = fields.Float()
    amount = fields.Float(string='Bonus Amount', compute='get_bonus_amount')
    note = fields.Text()
    employee_id = fields.Many2one(comodel_name='hr.employee')
    department_id = fields.Many2one(comodel_name='hr.department', related='employee_id.department_id')
    contract_id = fields.Many2one(comodel_name='hr.contract', related='employee_id.contract_id')

    @api.depends('contract_id', 'value')
    def get_bonus_amount(self):
        for rec in self:
            rec.amount = 0.0
            if rec.bonus_type.type == 'hour':
                rec.amount = rec.value * rec.contract_id.hour_value
            elif rec.bonus_type.type == 'day':
                rec.amount = rec.value * rec.contract_id.day_value
            elif rec.bonus_type.type == 'fixed':
                rec.amount = rec.value
