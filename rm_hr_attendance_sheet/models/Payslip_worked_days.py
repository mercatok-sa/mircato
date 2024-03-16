from odoo import models, fields, api, _


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    custom_number_of_hours = fields.Float(string='Number of Hours', compute='get_no_of_hours')

    @api.depends('number_of_days')
    def get_no_of_hours(self):
        for rec in self:
            rec.custom_number_of_hours = (rec.number_of_days * rec.contract_id.resource_calendar_id.total_worked_hours)

    @api.depends('is_paid', 'is_credit_time', 'number_of_hours', 'payslip_id', 'contract_id.wage',
                 'payslip_id.sum_worked_hours')
    def _compute_amount(self):
        for worked_days in self.filtered(lambda wd: not wd.payslip_id.edited):
            if not worked_days.contract_id or worked_days.code == 'OUT':
                worked_days.amount = 0
                continue
            if worked_days.payslip_id.wage_type == "hourly":
                worked_days.amount = worked_days.payslip_id.contract_id.hourly_wage * (
                        worked_days.number_of_days * worked_days.contract_id.resource_calendar_id.total_worked_hours) \
                    if worked_days.is_paid else 0
            else:
                if worked_days.number_of_days > 0:
                    worked_days.amount = worked_days.payslip_id.contract_id.contract_wage / worked_days.number_of_days
                else:
                    worked_days.amount = 0
