# coding: utf-8
from odoo import models, fields, api, _
# from odoo.exceptions import AccessError, UserError, ValidationError
# from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
# from datetime import datetime, time
from dateutil.relativedelta import relativedelta


class HrLeaveRequest(models.Model):
    _inherit = 'hr.leave'

    expected_leave = fields.Float(string="Expected Number Of leaves", compute='_compute_leaves_count', store=True)
    # duration_display = fields.Float()
    is_payed_in_advance = fields.Boolean(string="Is Payed in Advance")
    compute_full_days = fields.Boolean(string="Include Weekend Days", default=False)

    @api.depends('holiday_status_id', 'employee_id', 'request_date_to')
    def _compute_leaves_count(self):
        for rec in self:
            diff = 0
            allocation_obj = self.env['hr.employee'].search([('id', '=', rec.employee_id.id)], limit=1)
            allocation_days = allocation_obj.remaining_leaves
            if rec.request_date_to:
                diff = (rec.request_date_to - fields.Date.today()).days
            if allocation_days and diff:
                rec.expected_leave = allocation_days + diff * (30 / 365)
            elif allocation_days:
                rec.expected_leave = allocation_days
            elif diff:
                rec.expected_leave = diff * (30 / 365)

    # @api.constrains('state', 'number_of_days', 'holiday_status_id')
    # def _check_holidays(self):
    #     for holiday in self:
    #         if holiday.holiday_type != 'employee' or not holiday.employee_id:
    #             continue
    #         if holiday.number_of_days_display > holiday.expected_leave:
    #             raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
    #                                     'Please also check the leaves waiting for validation.'))

    def get_workday(self, index):
        values = [('0', 'Monday'),
                  ('1', 'Tuesday'),
                  ('2', 'Wednesday'),
                  ('3', 'Thursday'),
                  ('4', 'Friday'),
                  ('5', 'Saturday'),
                  ('6', 'Sunday')]
        return str(dict(values)[(index)])

    def get_week_ends_and_working_days(self, working_schedule=False):
        weekends = []
        working_days = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if working_schedule:
            for attend_day in working_schedule[0].attendance_ids:
                if self.get_workday(attend_day.dayofweek) not in working_days:
                    working_days.append(self.get_workday(attend_day.dayofweek))
            weekends = list(set(days) - set(working_days))
        return [weekends, working_days]

    def _check_weekend_days(self, from_date, to_date, weekend_days):
        weekly_off_count = 0
        weekly_start_calc_dt = from_date
        while weekly_start_calc_dt <= to_date:
            if self.get_workday(str(weekly_start_calc_dt.weekday())) in weekend_days:
                weekly_off_count += 1
            weekly_start_calc_dt = weekly_start_calc_dt + relativedelta(days=1)
        return weekly_off_count

    # def _get_number_of_days_details(self, date_from, date_to, employee_id, compute_leaves=False):
    #     """ Returns a float equals to the timedelta between two dates given as string."""
    #     employee = self.env['hr.employee'].browse(employee_id)
    #     working_schedule = employee.resource_calendar_id
    #     week_end_days_count = self._check_weekend_days(date_from, date_to,
    #                                                    self.get_week_ends_and_working_days(
    #                                                        working_schedule=working_schedule)[0])
    #     if employee_id and compute_leaves == True:
    #         employee = self.env['hr.employee'].browse(employee_id)
    #         return employee._get_work_days_data_batch(date_from, date_to)[employee.id]['days'] + week_end_days_count
    #     if employee_id and compute_leaves == False:
    #         employee = self.env['hr.employee'].browse(employee_id)
    #         return employee._get_work_days_data_batch(date_from, date_to)[employee.id]['days']
    #     today_hours = self.env.company.resource_calendar_id.get_work_hours_count(
    #         datetime.combine(date_from.date(), time.min), datetime.combine(date_from.date(), time.max), False)
    #     hours = self.env.company.resource_calendar_id.get_work_hours_count(date_from, date_to)
    #     return {'days': hours / (today_hours or HOURS_PER_DAY), 'hours': hours}
    #
    # @api.depends('date_from', 'date_to', 'employee_id', 'compute_full_days')
    # @api.onchange('date_from', 'date_to', 'employee_id', 'compute_full_days')
    # def _onchange_leave_dates(self):
    #     for rec in self:
    #         if rec.employee_id and rec.date_from and rec.date_to and rec.compute_full_days:
    #             rec.number_of_days = self._get_number_of_days_details(rec.date_from, rec.date_to, rec.employee_id.id,
    #                                                                   compute_leaves=True)
    #         elif rec.employee_id and rec.date_from and rec.date_to:
    #             rec.number_of_days = self._get_number_of_days_details(rec.date_from, rec.date_to, rec.employee_id.id,
    #                                                                   compute_leaves=False)

            # else:
            #     rec.number_of_days = 0.0


class HolidaysAllocationInherit(models.Model):
    _inherit = 'hr.leave.allocation'

    _sql_constraints = [
        ('type_value',
         "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or "
         "(holiday_type='category' AND category_id IS NOT NULL) or "
         "(holiday_type='department' AND department_id IS NOT NULL) or "
         "(holiday_type='company' AND mode_company_id IS NOT NULL))",
         "The employee, department, company or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('duration_check', "CHECK ( 1=1 )", "The number of days must be greater than 0."),
        ('number_per_interval_check', "CHECK(number_per_interval > 0)",
         "The number per interval should be greater than 0"),
        ('interval_number_check', "CHECK(interval_number > 0)", "The interval number should be greater than 0"),
    ]
