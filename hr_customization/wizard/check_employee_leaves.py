# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _


class CheckEmployeeLeaves(models.TransientModel):
    _name = "check.employee.leaves"

    employee_id = fields.Many2one('hr.employee', string="Employee")
    date = fields.Date(string="Date", default=fields.Date.context_today)

    def get_employee_leaves(self):
        employee_obj = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        diff_days = (self.date - fields.Date.today()).days
        employee_obj.all_leaves_from_report = (diff_days * (30 / 365))
        return {
            'name': _('Employee Leaves'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'hr.employee',
            'view_id': self.env.ref('hr_customization.employee_leaves_tree_view').id,
            'target': 'current',
            'domain': [('id', '=', self.employee_id.id)],
        }
