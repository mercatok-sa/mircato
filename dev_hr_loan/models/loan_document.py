# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime, timedelta


class DevLoanDocument(models.Model):
    _name = 'dev.loan.document'

    sequ_name = fields.Char(string='Sequence', readonly=True, copy=False)
    name = fields.Char(string='Name', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    loan_id = fields.Many2one('employee.loan', string='Loan')
    document = fields.Binary(string='Document', required=True, copy=False)
    date = fields.Date(string='Date', default=fields.Date.today())
    note = fields.Text(string='Note')

    @api.model
    def create(self, vals):
        vals['sequ_name'] = self.env['ir.sequence'].next_by_code(
            'dev.loan.document') or 'LOAN/DOC/'
        result = super(DevLoanDocument, self).create(vals)
        return result
