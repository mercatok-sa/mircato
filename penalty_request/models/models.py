# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class PenaltyRequest(models.Model):
    _name = "penalty.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", default="New", readonly=True, copy=False)
    state = fields.Selection(string="", selection=[('draft', 'Draft'),
                                                   ('confirmed', 'Confirmed'),
                                                   ('rejected', 'Rejected')], required=False, default='draft')

    def confirm_button(self):
        for rec in self:
            rec.state = 'confirmed'

    def reject_button(self):
        for rec in self:
            rec.state = 'rejected'

    def d_manager_confirm(self):
        for rec in self:
            res_user = rec.env['res.users'].search([('id', '=', rec._uid)])
            if rec.env.user.id == rec.employee_id.parent_id.user_id.id:
                rec.write({
                    'state': 'hr_manager'
                })
            elif res_user.has_group('hr.group_hr_user'):
                rec.write({
                    'state': 'hr_manager'
                })
            else:
                raise ValidationError("Only Employee Manger OR HR Manager Can Create That! ")

    def hr_manager_confirm(self):
        for rec in self:
            rec.state = 'accounting'

    def accounting_confirm(self):
        for rec in self:
            res_user = rec.env['res.users'].search([('id', '=', rec._uid)])
            if res_user.has_group('account.group_account_manager'):
                rec.state = 'confirm'
            else:
                raise ValidationError("Only Account Manger Can Approve That! ")

    def reject(self):
        self.state = 'rejected'

    @api.model
    def create(self, vals):
        vals['name'] = (self.env['ir.sequence'].next_by_code('penalty.request')) or 'New'
        return super(PenaltyRequest, self).create(vals)

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name", required=False, )
    request_date = fields.Date(string="Today Date", required=False, default=fields.Date.context_today)
    penalty_amount = fields.Float(string="Penalty Amount / Days", required=False, )
    penalty_type = fields.Selection(string="", selection=[('amount', 'Amount'), ('days', 'Days'), ], required=False, )
    penalty_amount_amount = fields.Float(string="Penalty Amount", required=False, )
    penalty_amount_days = fields.Float(string="Penalty Days", required=False, )
    num_lines = fields.Integer(string="No Of Lines", required=False, )
    reason = fields.Text(string="Reason", required=False)
    penalty_ids = fields.One2many('penalty.request.payment', 'penalty_id', 'Employee Payments')
    contract_id = fields.Many2one(string="", required=False, related="employee_id.contract_id")
    day_value = fields.Float(string="", required=False, compute="_compute_day_value")

    @api.depends('employee_id', 'contract_id')
    def _compute_day_value(self):
        for rec in self:
            if rec.employee_id and rec.contract_id:
                rec.day_value = rec.contract_id.wage / 26
            else:
                rec.day_value = 0.0

    def generate_payment_date(self):
        date_start = self.request_date
        if self.penalty_type == 'amount':
            if self.penalty_amount_amount and self.num_lines and self.employee_id:
                self.penalty_ids = False
                for i in range(1, self.num_lines + 1):
                    payment_time = {
                        'name': 'Penalty Request',
                        'date': date_start,
                        'days': 0.0,
                        'amount': self.penalty_amount_amount / self.num_lines,
                        'penalty_id': self.id,
                        'paid': False,
                    }
                    date_start += relativedelta(months=+1)
                    self.penalty_ids.create(payment_time)

        if self.penalty_type == 'days':
            if not self.employee_id.contract_id:
                raise ValidationError(
                    "Sorry.. This Employee Dont Have Contract, you can choose Penalty type amount, or create contract for this employee")
            else:
                if self.penalty_amount_days and self.employee_id:
                    self.penalty_ids = False
                    payment_time = {
                        'name': 'Penalty Request',
                        'date': date_start,
                        'days': self.penalty_amount_days,
                        'amount': self.day_value * self.penalty_amount_days,
                        'penalty_id': self.id,
                        'paid': False,
                    }
                    self.penalty_ids.create(payment_time)


class HrLoanDatePayment(models.Model):
    _name = "penalty.request.payment"
    _rec_name = 'date'

    days = fields.Integer(string="", required=False, )
    name = fields.Char(string="", required=False, )
    date = fields.Date()
    amount = fields.Float('Amount')
    penalty_id = fields.Many2one('penalty.request', "Loan")
    employee_id = fields.Many2one('hr.employee', related='penalty_id.employee_id', store=True)
    paid = fields.Boolean(string="", default=False)
    paid_b = fields.Boolean(string="", default=False)
