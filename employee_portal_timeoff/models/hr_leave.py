# See LICENSE file for full copyright and licensing details.

import random
from odoo import api, fields, models, _
from datetime import datetime, time

from odoo.exceptions import AccessDenied
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class EmpPortalTimeOff(models.Model):
    _inherit = "hr.leave"

    def update_timeoff_portal(self, values):
        dt_from = values['from']
        dt_to = values['to']
        if dt_from:
            dt_from = datetime.strptime(dt_from, DF).date()
        if dt_to:
            dt_to = datetime.strptime(dt_to, DF).date()
        for timeoff in self:
            timeoff_values = {
                'name': values['description'],
                'holiday_status_id': int(values['timeoff_type']),
                'request_date_from': dt_from,
                'request_date_to': dt_to,
                'request_unit_half': values['half_day'],
                'request_unit_hours': values['custom_hours'],
                'request_hour_from': values['request_hour_from'],
                'request_hour_to': values['request_hour_to'],
                'request_date_from_period': values['request_date_from_period'],
            }
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                if timeoff_rec:
                    timeoff_rec.sudo().write(timeoff_values)
                    timeoff_rec._compute_date_from_to()

    @api.model
    def create_timeoff_portal(self, values):
        if not self.env.user.employee_id:
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        if not (values['description'] and values['timeoff_type'] and values['from'] and values['to'] and
                values['delegation_id']):
            return {
                'errors': _('All fields are required !')
            }
        values = {
            'name': values['description'],
            'holiday_status_id': int(values['timeoff_type']),
            'request_date_from': values['from'],
            'request_date_to': values['to'],
            'request_unit_half': values['half_day'],
            'request_unit_hours': values['custom_hours'],
            'request_hour_from': values['request_hour_from'],
            'request_hour_to': values['request_hour_to'],
            'request_date_from_period': values['request_date_from_period'],
            'delegation_id': values['delegation_id'],
        }
        tmp_leave = self.env['hr.leave'].sudo().new(values)
        tmp_leave._compute_date_from_to()
        values = tmp_leave._convert_to_write(tmp_leave._cache)
        mytimeoff = self.env['hr.leave'].sudo().create(values)
        return {
            'id': mytimeoff.id
        }
