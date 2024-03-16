from odoo import fields, models, api, _


class HrPayrollIndex(models.TransientModel):
    _inherit = 'hr.payroll.index'

    next_date_increase_salary = fields.Date()

    def action_confirm(self):
        res = super(HrPayrollIndex, self).action_confirm()
        for line in self.contract_ids:
            if self.next_date_increase_salary and self.percentage:
                line.update({'next_date_increase_salary': self.next_date_increase_salary,
                             'percentage_index': self.percentage})
        return res
