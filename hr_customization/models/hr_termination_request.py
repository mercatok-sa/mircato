# coding: utf-8
from odoo import models, fields, api, _
import datetime
from odoo.exceptions import AccessError, UserError, ValidationError


class HrTerminationRequest(models.Model):
    _name = 'hr.termination.request'
    _rec_name = 'employee_id'

    def get_emp_with_contract(self):
        employees = []
        contract_objects = self.env['hr.contract'].sudo().search(
            [('employee_id', '!=', False), ('state', 'in', ['draft', 'open', 'pending'])])
        for contract in contract_objects:
            employees.append(contract.employee_id.id)
        return [('id', 'in', employees)]

    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'), ('terminated', 'Terminated'), ('canceled', 'Canceled')],
                             default='draft')
    employee_id = fields.Many2one('hr.employee', string="Employee", domaon=get_emp_with_contract)
    rule_id = fields.Many2one('hr.config.rules', string="Rule Name", related='employee_id.contract_id.rule_id',
                              readonly=1)
    notes = fields.Text(string="Notes")
    last_date = fields.Date(string="Last Date")
    number_of_day = fields.Float(string="", required=False, )
    number_of_year = fields.Float(string="", required=False, )
    percentage_value = fields.Float(string="", required=False, default=100, readonly=1)

    @api.onchange('last_date')
    @api.constrains('last_date')
    def onchange_get_num_of_year(self):
        for rec in self:
            hr_contract_obj = rec.employee_id.contract_id
            if hr_contract_obj:
                contract_start_days = hr_contract_obj.date_start
                termination_days = rec.last_date
                diff_dayes = termination_days - contract_start_days
                print(diff_dayes.days)
                diff_years = diff_dayes.days / 365
                rec.number_of_year = round(diff_years, 1)

    def get_employee_termination(self):
        for rec in self:
            termination_rule_obj = rec.rule_id
            hr_contract_obj = rec.employee_id.contract_id
            unpaid_type = self.env['hr.leave.type'].search([('is_unpiad_leave', '=', True)])
            unpaid_leave = self.env['hr.leave'].search(
                [('employee_id', '=', rec.employee_id.id), ('holiday_status_id', 'in', unpaid_type.ids)])
            number_day_unpaid = sum(unpaid_leave.mapped('number_of_days_display'))
            if hr_contract_obj:
                # contract_start_year = hr_contract_obj.date_start.year
                contract_start_days = hr_contract_obj.date_start
                termination_days = rec.last_date
                # current_year = datetime.datetime.now().year
                # diff_years = termination_year - contract_start_year
                diff_dayes = termination_days - contract_start_days
                rec.number_of_day = diff_dayes.days
                if rec.number_of_day > 468:
                    rec.number_of_day = 468
                rec.number_of_day = rec.number_of_day - number_day_unpaid
                diff_years = rec.number_of_day / 365
                print("diff_years ===", (diff_years))
                all_years = diff_dayes.days / 365
                print("all_years ===", all_years)
                salary_per_day = hr_contract_obj.wage / termination_rule_obj.month_work_days
                if termination_rule_obj:
                    dayes_per_year1 = 0.0
                    dayes_per_year2 = 0.0
                    for termination in termination_rule_obj.terminations_rule_ids:
                        if float(all_years) > termination.termination_rang_start:
                            print("termination_rang_start ==", termination.termination_rang_start)
                            # if all_years <= 3.0:
                            #     raise ValidationError('The Period to employee Not more than 3 years!')
                            if termination.termination_rang_start == 0.0 and termination.termination_rang_end == 5.0:
                                if all_years > 0.0:
                                    dayes_per_year1 = termination.termination_rang_end * termination.termination_days_per_year
                                    print("dayes_per_year1 ===", dayes_per_year1)
                            if termination.termination_rang_start == 5.0:
                                if all_years > 5.0:
                                    print(rec.number_of_year - 5 / 365)
                                    last_years = rec.number_of_year - 5
                                    dayes_per_year2 = last_years * termination.termination_days_per_year
                                    print("dayes_per_year2 ===", dayes_per_year2)

                        all_days_year = (dayes_per_year1 + dayes_per_year2) - number_day_unpaid
                        static_days_limit = all_days_year if all_days_year <= 468 else 468
                        rec.number_of_day = static_days_limit
                        print(all_days_year)
                        hr_contract_obj.employee_id.update({
                            'termination_amount': (salary_per_day * static_days_limit) * rec.percentage_value / 100
                        })
                        rec.state = 'terminated'
                        # todo old solution
                        # if termination.termination_rang_start <= float(diff_years) < termination.termination_rang_end:
                        #     hr_contract_obj.employee_id.update({
                        #         'termination_amount':
                        #             (
                        #                         termination.termination_days_per_year * float(diff_years)) * salary_per_day * termination.deduction_amount})

    def termination_cancel(self):
        for rec in self:
            rec.state = 'canceled'
