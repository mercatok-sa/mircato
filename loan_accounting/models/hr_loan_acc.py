# -*- coding: utf-8 -*-
import time
from odoo import models, api, fields
from odoo.exceptions import UserError


class HrLoanAcc(models.Model):
    _inherit = 'hr.loan'

    employee_account_id = fields.Many2one('account.account', string="Loan Account")

    treasury_journal_id = fields.Many2one('account.journal', string="Treasury journal",
                                          domain=[('type', 'in', ('bank', 'cash'))])
    journal_id = fields.Many2one('account.journal', string="Journal", domain=[('type', '=', 'general')])

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('waiting_approval_2', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', copy=False, )

    def action_approve(self):
        """This create account move for request.
            """
        loan_approve = self.env['ir.config_parameter'].sudo().get_param('account.loan_approve')
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
        if not contract_obj:
            raise UserError('You must Define a contract for employee')
        if not self.loan_lines:
            raise UserError('You must compute installment before Approved')
        if loan_approve:
            self.write({'state': 'waiting_approval_2'})
        else:
            if not self.employee_account_id or not self.treasury_journal_id or not self.journal_id:
                raise UserError("You must enter employee account & Treasury journal and journal to approve ")
            if not self.loan_lines:
                raise UserError('You must compute Loan Request before Approved')
            timenow = time.strftime('%Y-%m-%d')
            for loan in self:
                amount = loan.loan_amount
                loan_name = loan.employee_id.name
                reference = loan.name
                journal_id = loan.journal_id.id
                debit_account_id = loan.employee_account_id.id

                pay_account_id = loan.treasury_journal_id.outbound_payment_method_line_ids.mapped('payment_account_id')
                if pay_account_id:
                    credit_account_id = pay_account_id.id
                else:
                    credit_account_id = self.company_id.account_journal_payment_credit_account_id.id

                debit_vals = {
                    'name': 'Debit - ' + loan_name + 'pay loan value',
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'partner_id': loan.employee_id.address_home_id.id,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'loan_id': loan.id,
                }
                credit_vals = {
                    'name': 'Credit - ' + loan_name + 'pay loan value',
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'partner_id': loan.employee_id.address_home_id.id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'loan_id': loan.id,
                }
                vals = {
                    'name': 'Loan For' + ' ' + loan_name,
                    'narration': loan_name,
                    'ref': reference,
                    'journal_id': journal_id,
                    'date': timenow,
                    'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                }
                move = self.env['account.move'].create(vals)
                move.post()
            self.write({'state': 'approve'})
        return True

    def action_double_approve(self):
        """This create account move for request in case of double approval.
            """
        if not self.employee_account_id or not self.treasury_journal_id or not self.journal_id:
            raise UserError("You must enter employee account & Treasury journal and journal to approve ")
        if not self.loan_lines:
            raise UserError('You must compute Loan Request before Approved')
        timenow = time.strftime('%Y-%m-%d')
        for loan in self:
            amount = loan.loan_amount
            loan_name = loan.employee_id.name
            reference = loan.name
            journal_id = loan.journal_id.id
            debit_account_id = loan.employee_account_id.id

            pay_account_id = loan.treasury_journal_id.outbound_payment_method_line_ids.mapped('payment_account_id')
            if pay_account_id:
                credit_account_id = pay_account_id.id
            else:
                credit_account_id = self.company_id.account_journal_payment_credit_account_id.id

            debit_vals = {
                'name': 'Debit - ' + loan_name + 'pay loan value',
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'partner_id': loan.employee_id.address_home_id.id,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'loan_id': loan.id,
            }
            credit_vals = {
                'name': 'Credit - ' + loan_name + 'pay loan value',
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'partner_id': loan.employee_id.address_home_id.id,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'loan_id': loan.id,
            }
            vals = {
                'name': 'Loan For' + ' ' + loan_name,
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.post()
        self.write({'state': 'approve'})
        return True
