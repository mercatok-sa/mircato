# coding: utf-8
from dateutil import relativedelta

from odoo import models, fields, api, _
from datetime import datetime
from collections import namedtuple
from odoo.tools.float_utils import float_round
import datetime
from collections import defaultdict
from datetime import timedelta
from pytz import utc

from odoo import api, fields, models
from odoo.tools import float_utils

# This will generate 16th of days
ROUNDING_FACTOR = 16


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    all_leaves_count = fields.Float(string="Number of Leaves")
    all_leaves_from_report = fields.Float(string="Number of Leaves")
    check_report_leave = fields.Boolean(string="Report Leave")
    annual_leave_compute_type = fields.Selection(string="Annual Leave Compute Type",
                                                 selection=[('all_leaves', 'All Leaves Computed'),
                                                            ('some_leaves', 'Some Leaves Computed')])
    sick_leave_remaining_days = fields.Float(string="Sick Leave Remaining Days")

    termination_amount = fields.Float(string="Termination Amount")
    resignation_amount = fields.Float(string="Resignation Amount")
    rule_id = fields.Many2one('hr.config.rules', string="Rule Name")
    leaves_count = fields.Float('Number of Time Off', compute='_compute_remaining_leaves')
    indemnity_liability = fields.Float(string="Indemnity Liability")

    @api.model
    def get_employee_annual_leave(self):
        for rec in self.env['hr.employee'].search([]):
            contract_obj = self.env['hr.contract'].search([('id', '=', rec.contract_id.id), ('state', '=', 'open')],
                                                          limit=1)
            rec.all_leaves_count += (contract_obj.annual_leave_per_day / 365)

    def get_work_days_data(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a dict {'days': n, 'hours': h} containing the
            quantity of working time expressed as days and as hours.
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetimes are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        # total hours per day: retrieve attendances with one extra day margin,
        # in order to compute the total hours on the first and last days
        from_full = from_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)
        intervals = calendar._attendance_intervals_batch(from_full, to_full, resource)
        day_total = defaultdict(float)
        for start, stop, meta in intervals:
            day_total[start.date()] += (stop - start).total_seconds() / 3600

        # actual hours per day
        if compute_leaves:
            intervals = calendar._work_intervals(from_datetime, to_datetime, resource, domain)
        else:
            intervals = calendar._attendance_intervals_batch(from_datetime, to_datetime, resource)
        day_hours = defaultdict(float)
        for start, stop, meta in intervals:
            day_hours[start.date()] += (stop - start).total_seconds() / 3600

        # compute number of days as quarters
        days = sum(
            float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[day]) / ROUNDING_FACTOR
            for day in day_hours
        )
        return {
            'days': days,
            'hours': sum(day_hours.values()),
        }

    @api.model
    def get_employee_termination_and_resignation_amount(self):
        employee_obj = self.env['hr.employee'].search([])
        rule_obj = self.env['hr.config.rules'].search([])
        for rec in employee_obj:
            hr_contract_obj = self.env['hr.contract'].search(
                [('employee_id', '=', rec.id), ('state', 'not in', ['close', 'cancel'])])
            if rule_obj:
                rule_obj = self.env['hr.config.rules'].search([])[0]
            if hr_contract_obj:
                contract_start_year = (hr_contract_obj.date_start).year
                contract_start_month = (hr_contract_obj.date_start).month
                current_year = datetime.datetime.now().year
                current_month = datetime.datetime.now().month
                diff_years = current_year - contract_start_year
                diff_month = current_month - contract_start_month
                diff_years += diff_month / 12
                salary_per_day = hr_contract_obj.wage / 26
                total = 0
                diff = 0
                total_regis = 0
                if rule_obj:
                    for termination in rule_obj.terminations_rule_ids:
                        if termination.termination_rang_start <= diff_years < termination.termination_rang_end:
                            newdiff = diff_years - diff
                            second_rule_value = (
                                                        termination.termination_days_per_year * newdiff * salary_per_day) * termination.deduction_amount
                            second_rule_value += total

                            hr_contract_obj.employee_id.update({'termination_amount': second_rule_value})
                            rec.state = 'terminated'
                        else:
                            diff += (termination.termination_rang_end - termination.termination_rang_start)
                            diff2 = (termination.termination_rang_end - termination.termination_rang_start)
                            total += (
                                             termination.termination_days_per_year * diff2 * salary_per_day) * termination.deduction_amount
                if rule_obj:
                    counter = 0
                    diff_regis22 = 0
                    for resignation in rule_obj.resignation_rule_ids:
                        if resignation.resignation_rang_start <= diff_years < resignation.resignation_rang_end:

                            newdiff = diff_years - diff_regis22
                            second_regis_value = (resignation.resignation_days_per_year * newdiff)
                            second_regis_value += total_regis
                            final_regis_value = second_regis_value * salary_per_day * resignation.deduction_amount
                            hr_contract_obj.employee_id.update({'resignation_amount': final_regis_value})
                            rec.state = 'resigned'
                            break
                        else:
                            if counter > 0:
                                diff_regis = resignation.resignation_rang_end
                                diff_regis2 = resignation.resignation_rang_end
                                diff_regis22 += resignation.resignation_rang_end
                                total_regis += (resignation.resignation_days_per_year * diff_regis)

                            else:
                                counter += 1

    @api.model
    def get_employee_indemnity_liability(self):
        for rec in self.env['hr.employee'].search([]):
            if rec.contract_id:
                worked_months = 0.0
                contract_start = rec.contract_id.date_start
                salary_per_day = rec.contract_id.wage / 26

                # Get related termination request
                related_termination_request = self.env['hr.termination.request'].search([('employee_id', '=', rec.id)],
                                                                                        order='last_date desc', limit=1)
                if related_termination_request:
                    termination_date = related_termination_request.last_date

                    # Remove leave from calculation
                    leave = sum(self.env['hr.leave'].search([('holiday_status_id.calculate_in_ter_resi', '=', True),
                                                             ('state', '=', 'validate'),
                                                             ('employee_id', '=', rec.id)]).mapped('number_of_days'))
                    if leave:
                        termination_date -= timedelta(days=leave)

                    diff = relativedelta.relativedelta(termination_date, contract_start)
                    years = diff.years
                    months = diff.months
                    days = diff.days

                    termination_year = related_termination_request.last_date.year
                    diff_years = termination_year - rec.contract_id.date_start.year

                    if related_termination_request.rule_id:
                        if years > 0:
                            worked_months = 12 * years
                        if months:
                            worked_months += months

                        for termination in related_termination_request.rule_id.terminations_rule_ids:
                            if termination.termination_rang_start <= diff_years < termination.termination_rang_end:
                                if days:
                                    worked_months += (termination.termination_days_per_year / 12) / 30 * days
                                amount = (termination.termination_days_per_year / 12) * worked_months * salary_per_day
                                rec.contract_id.employee_id.update({'indemnity_liability': amount})

        # employee_obj = self.env['hr.employee'].search([])
        # rule_obj = self.env['hr.config.rules'].search([])
        # for rec in employee_obj:
        #     hr_contract_obj = rec.contract_id
        #     if rule_obj:
        #         rule_obj = self.env['hr.config.rules'].search([])[0]
        #     if hr_contract_obj:
        #         contract_start_year = hr_contract_obj.date_start.year
        # current_year = datetime.datetime.now().year
        #         diff_years = current_year - contract_start_year
        #         salary_per_day = hr_contract_obj.wage / 26
        #         if rule_obj:
        #             for termination in rule_obj.terminations_rule_ids:
        #                 if termination.termination_rang_start <= diff_years < termination.termination_rang_end:
        #                     hr_contract_obj.employee_id.update({
        #                         'indemnity_liability':
        #                             (
        #                                     termination.termination_days_per_year * diff_years) * salary_per_day * termination.deduction_amount})


class HrEmployeesPublic(models.Model):
    _inherit = 'hr.employee.public'

    all_leaves_count = fields.Float(string="Number of Leaves")
    all_leaves_from_report = fields.Float(string="Number of Leaves")
    check_report_leave = fields.Boolean(string="Report Leave")
    annual_leave_compute_type = fields.Selection(string="Annual Leave Compute Type",
                                                 selection=[('all_leaves', 'All Leaves Computed'),
                                                            ('some_leaves', 'Some Leaves Computed')])
    sick_leave_remaining_days = fields.Float(string="Sick Leave Remaining Days")

    termination_amount = fields.Float(string="Termination Amount")
    resignation_amount = fields.Float(string="Resignation Amount")
    rule_id = fields.Many2one('hr.config.rules', string="Rule Name")
    leaves_count = fields.Float('Number of Time Off', compute='_compute_remaining_leaves')
    indemnity_liability = fields.Float(string="Indemnity Liability")
