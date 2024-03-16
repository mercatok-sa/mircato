# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class InstallmentAnalyticLineView(models.Model):
    _name = 'employee.loan.report.view'
    _table = 'employee_loan_report_view'
    _description = "Employee Loan View"
    _auto = False
    _rec_name = 'date'

    name = fields.Char('Loan')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date = fields.Date('Date')
    department_id = fields.Many2one('hr.department', string='Department')
    manager_id = fields.Many2one('hr.employee', string='Manager')
    job_id = fields.Many2one('hr.job', string='Job Position')
    loan_type_id = fields.Many2one('employee.loan.type', string='Loan Type')
    term = fields.Integer('Term')
    n_paid_amount = fields.Float('Paid Amount')
    n_remaing_amount = fields.Float('Remaining Amount')

    loan_amount = fields.Float('Loan Amount')
    state = fields.Selection([('draft', 'Draft'),
                              ('request', 'Submit Request'),
                              ('dep_approval', 'Department Approval'),
                              ('hr_approval', 'HR Approval'),
                              ('paid', 'Paid'),
                              ('done', 'Done'),
                              ('close', 'Close'),
                              ('reject', 'Reject'),
                              ('cancel', 'Cancel')], string='State')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'employee_loan_report_view')
        self._cr.execute("""
          CREATE OR REPLACE VIEW employee_loan_report_view AS
          SELECT el.id,
                 el.name,
                 el.employee_id,
                 el.date,
                 el.department_id,
                 el.manager_id,
                 el.job_id,
                 el.loan_type_id,
                 el.term,
                 el.state,
                 el.loan_amount,
                 el.n_paid_amount,
                 el.n_extra_in_amount,
                 el.n_remaing_amount FROM employee_loan el where el.state in ('close','done'); """)
