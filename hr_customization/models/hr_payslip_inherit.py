# coding: utf-8
from odoo import models, fields, api, _
from datetime import datetime, time
from collections import namedtuple
from pytz import timezone
from odoo.exceptions import AccessError, UserError, ValidationError


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    total_sick_leave_amount = fields.Float(string="Total Sick Leave Amount", compute='_calc_sick_deduction_amount',
                                           store=True)
    total_annual_leave_amount = fields.Float(string="Total annual Leave Amount", compute='_calc_sick_deduction_amount')
    total_basic_salary = fields.Float(string="Total Basic Salary", compute='_calc_sick_deduction_amount')
    current_month = fields.Date(string="Current Month", compute='_calc_sick_deduction_amount')
    next_month = fields.Date(string="Next Month", compute='_calc_sick_deduction_amount')
    annual_leaves_count = fields.Float(compute='_calc_annual_leaves_count', string='Annual Leaves count (days)')

    def payslip_mass_mailing(self):
        view_id = self.env.ref('hr_customization.view_payslip_mass_mailing').id
        return {'type': 'ir.actions.act_window',
                'name': _('Payslip Mass Mailing'),
                'res_model': 'payslip.mass.mailing',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']]}

    def check_cancel_action(self):
        for rec in self:
            if rec.state != 'draft' and rec.check_printing_payment_method_selected == True:
                rec.check_cancel()
            else:
                raise ValidationError(_('You can not make Check Cancel in Draft state .'))

    def get_sick_leave_days(self, date_from, date_to):
        for rec in self:
            total_sick_leave_days = 0.0
            if rec.date_from and rec.date_to and rec.employee_id:
                sick_leave_recs = self.env['hr.leave'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('holiday_status_id.sick_leave', '=', True),
                    ('state', 'in', ['validate']),
                    '|',
                    '|',
                    '&',
                    ('date_from', '<=', date_from), ('date_to', '>=', date_from),
                    '&',
                    ('date_from', '<=', date_to), ('date_to', '>=', date_to),
                    '|',
                    '&',
                    ('date_from', '>=', date_from), ('date_to', '<=', date_to),
                    '&',
                    ('date_from', '<=', date_from), ('date_to', '>=', date_to),
                ])
                if sick_leave_recs:
                    for leave in sick_leave_recs:
                        total_sick_leave_days += leave.number_of_days
            return total_sick_leave_days

    @api.depends('date_from', 'date_to', 'employee_id', 'contract_id')
    def _calc_annual_leaves_count(self):
        for rec in self:
            count = 0.0
            salary_per_day = rec.contract_id.wage / 26
            if rec.date_from and rec.date_to and rec.employee_id:
                annual_leave_recs = self.env['hr.leave'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('holiday_status_id.annual_leave', '=', True),
                    ('state', 'in', ['validate']),
                    '|',
                    '|',
                    '&',
                    ('date_from', '<=', rec.date_from), ('date_to', '>=', rec.date_from),
                    '&',
                    ('date_from', '<=', rec.date_to), ('date_to', '>=', rec.date_to),
                    '|',
                    '&',
                    ('date_from', '>=', rec.date_from), ('date_to', '<=', rec.date_to),
                    '&',
                    ('date_from', '<=', rec.date_from), ('date_to', '>=', rec.date_to),
                ])

                if annual_leave_recs:
                    for leave in annual_leave_recs:
                        count += leave.number_of_days
            rec.annual_leaves_count = count * salary_per_day

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), time.max)

            # compute leave days
            leaves = {}
            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)
            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to,
                                                                   calendar=contract.resource_calendar_id)
            for day, hours, leave in day_leave_intervals:
                holiday = leave[:1].holiday_id
                current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                    'name': holiday.holiday_status_id.name or _('Global Leaves'),
                    'sequence': 5,
                    'code': holiday.holiday_status_id.name or 'GLOBAL',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                })
                current_leave_struct['number_of_hours'] += hours
                work_hours = calendar.get_work_hours_count(
                    tz.localize(datetime.combine(day, time.min)),
                    tz.localize(datetime.combine(day, time.max)),
                    compute_leaves=False,
                )
                if work_hours:
                    current_leave_struct['number_of_days'] += hours / work_hours

            # compute worked days
            work_data = contract.employee_id.get_work_days_data(day_from, day_to,
                                                                calendar=contract.resource_calendar_id)
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.extend(leaves.values())
        return res

    @api.depends('date_from', 'date_to', 'employee_id', 'worked_days_line_ids')
    def _calc_sick_deduction_amount(self):
        for rec in self:
            first_day_in_year = datetime.now().date().replace(month=1, day=1)
            last_day_in_year = datetime.now().date().replace(month=12, day=31)
            total_sick_leave_days = self.get_sick_leave_days(first_day_in_year, last_day_in_year)
            salary_per_day = rec.contract_id.wage / 26
            before_total_sick_leave_days = self.get_sick_leave_days(first_day_in_year, rec.date_from)
            total_sick_leave_days_in_period = self.get_sick_leave_days(rec.date_from, rec.date_to)
            sick_leave_value = 0.0
            diff_days = total_sick_leave_days - total_sick_leave_days_in_period
            sick_leave_obj = self.env['hr.leave'].search(
                [('employee_id', '=', rec.employee_id.id), ('holiday_status_id.sick_leave', '=', True),
                 ('holiday_type', '=', 'employee'), ('state', '=', 'validate')])
            sick_days = total_sick_leave_days
            if sick_leave_obj:
                diff_days = abs(diff_days)
                for i in sick_leave_obj[0].holiday_status_id.sick_leave_rules_ids:
                    if diff_days != 0 and sick_days >= 0:
                        if i.days_from <= diff_days <= i.days_to and total_sick_leave_days <= i.days_to:
                            rate = salary_per_day * i.deduction
                            sick_days = sick_days - i.days_to
                            if diff_days == i.days_from:
                                current_days = int(total_sick_leave_days - i.days_from + 1)
                            elif diff_days > i.days_from and diff_days <= i.days_to:
                                current_days = int(total_sick_leave_days - diff_days)
                            else:
                                current_days = int(i.days_to - diff_days)
                            sick_leave_value += rate * current_days
                            sick_days = sick_days - i.days_to
                    elif i.days_from <= diff_days <= i.days_to and total_sick_leave_days >= i.days_to:
                        if diff_days == i.days_from:
                            current_days = i.days_to - diff_days + 1
                        else:
                            current_days = i.days_to - diff_days
                        rate = salary_per_day * i.deduction
                        sick_leave_value += rate * current_days
                        diff_days = i.days_to + 1
                    elif diff_days == 0:
                        if i.days_from <= total_sick_leave_days_in_period <= i.days_to and total_sick_leave_days <= i.days_to:
                            rate = salary_per_day * i.deduction
                            if total_sick_leave_days_in_period == i.days_from:
                                current_days = int(total_sick_leave_days - i.days_from + 1)
                            elif i.days_from == 0 and total_sick_leave_days_in_period > i.days_from and total_sick_leave_days_in_period <= i.days_to:
                                current_days = int(total_sick_leave_days - i.days_from)
                            elif total_sick_leave_days_in_period > i.days_from and total_sick_leave_days_in_period <= i.days_to:
                                current_days = int(total_sick_leave_days - i.days_from + 1)
                            else:
                                current_days = int(i.days_to - total_sick_leave_days_in_period)
                            sick_leave_value += rate * current_days
                            break
                        elif i.days_from <= total_sick_leave_days_in_period <= i.days_to and total_sick_leave_days >= i.days_to:
                            if total_sick_leave_days_in_period == i.days_from:
                                current_days = i.days_to - total_sick_leave_days_in_period + 1
                            else:
                                current_days = i.days_to - total_sick_leave_days_in_period
                            rate = salary_per_day * i.deduction
                            sick_leave_value += rate * current_days
                            total_sick_leave_days_in_period = i.days_to + 1
                        elif i.days_from <= total_sick_leave_days_in_period >= i.days_to:
                            current_days = i.days_to - i.days_from
                            rate = salary_per_day * i.deduction
                            sick_leave_value += rate * current_days
                            total_sick_leave_days_in_period = i.days_to + 1
                rec.total_sick_leave_amount = sick_leave_value
