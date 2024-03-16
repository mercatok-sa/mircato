# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from datetime import datetime, timedelta
from collections import defaultdict


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    att_policy_id = fields.Many2one('hr.attendance.policy', string='Attendance Policy')

    def _get_work_hours(self, date_from, date_to, domain=None):
        date_from = datetime.combine(date_from, datetime.min.time())
        date_to = datetime.combine(date_to, datetime.max.time())
        work_data = defaultdict(int)

        # First, found work entry that didn't exceed interval.
        work_entries = self.env['hr.work.entry'].read_group(
            self._get_work_hours_domain(date_from, date_to, domain=domain, inside=True), ['hours:sum(duration)'],
            ['work_entry_type_id'])
        work_data.update({data['work_entry_type_id'][0]
                          if data['work_entry_type_id'] else False: data['work_entry_type_id_count'] * 8.0
                          for data in work_entries})

        # Second, find work entry that exceeds interval and compute right duration.
        work_entries = self.env['hr.work.entry'].search(
            self._get_work_hours_domain(date_from, date_to, domain=domain, inside=False))

        for work_entry in work_entries:
            date_start = max(date_from, work_entry.date_start)
            date_stop = min(date_to, work_entry.date_stop)
            if work_entry.work_entry_type_id.is_leave:
                contract = work_entry.contract_id
                calendar = contract.resource_calendar_id
                employee = contract.employee_id
                contract_data = employee._get_work_days_data_batch(
                    date_start, date_stop, compute_leaves=False, calendar=calendar)[employee.id]
                work_data[work_entry.work_entry_type_id.id] += contract_data.get('hours', 0)
            else:
                dt = date_stop - date_start
                work_data[work_entry.work_entry_type_id.id] += dt.days * 24 + dt.seconds / 3600  # Number of hours
        return work_data
