from odoo import fields, models, api, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_join_date = fields.Date()
    contract_start_training = fields.Date()
    contract_end_training = fields.Date()

    # Allowances
    housing_allowance = fields.Monetary()
    transportation_allowance = fields.Monetary()
    other_allowances = fields.Monetary()
    total_amount = fields.Monetary(compute='get_total_amount', string='Total Salary ')

    @api.depends('wage', 'housing_allowance', 'transportation_allowance', 'other_allowances')
    def get_total_amount(self):
        for item in self:
            item.total_amount = item.wage + item.housing_allowance + item.transportation_allowance + item.other_allowances

    workdays_hour = fields.Float()
    number_of_month_days = fields.Float(string='No. Month Days')
    hour_value = fields.Float(compute='compute_hour_value')
    day_value = fields.Float(compute='compute_day_value')

    def compute_day_value(self):
        for item in self:
            item.day_value = 0.0
            if item.wage and item.number_of_month_days:
                item.day_value = item.total_amount / item.number_of_month_days

    def compute_hour_value(self):
        for rec in self:
            rec.hour_value = 0.0
            if rec.day_value and rec.workdays_hour:
                rec.hour_value = rec.day_value / rec.workdays_hour

    medical_details = fields.Boolean()
    insurance_company = fields.Many2one(comodel_name='insurance.company')
    insurance_number = fields.Char()
    insurance_start_date = fields.Date()
    insurance_end_date = fields.Date()
