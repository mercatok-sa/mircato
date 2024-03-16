from odoo import fields, models, api, _
from datetime import date


class PenaltyRequest(models.Model):
    _inherit = 'penalty.request'

    def update_penalty_portal(self, values):
        penalty_values = {
            'emp_manager_opinion': values['emp_manager_opinion'],
            'emp_manager_feedback': values['emp_manager_feedback'],
            'employee_cause_of_penalty': values['employee_cause_of_penalty'],
            'employee_approve_of_cause': values['employee_approve_of_cause'],
            'employee_other_approve': values['employee_other_approve'],
            'hr_manager_feedback': values['hr_manager_feedback'],
        }
        if values['PenaltyID']:
            peanlty_rec = self.env['penalty.request'].sudo().browse(values['PenaltyID'])
            if peanlty_rec:
                peanlty_rec.sudo().write(penalty_values)
