from odoo import fields, models, api, _
from datetime import datetime


class Contract(models.Model):
    _inherit = 'hr.contract'

    next_date_increase_salary = fields.Date()
    percentage_index = fields.Float()

    def update_contract_salary(self):
        for item in self:
            if item.next_date_increase_salary and item.percentage_index:
                if item.next_date_increase_salary == datetime.now().date():
                    item.update({'wage': item.wage * (1 + item.percentage_index)})
