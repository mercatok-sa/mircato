# -*- coding: utf-8 -*-
import time
from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class HrLoanAcc(models.Model):
    _inherit = 'hr.loan'

    account_move_id = fields.Many2one('account.move', string='Journal Entry')
    payment_move_id = fields.Many2one('account.move', string='Payment')

    employee_account_id = fields.Many2one('account.account', string="Loan Account")
    treasury_journal_id = fields.Many2one('account.journal', string="Treasury journal",
                                          domain=[('type', 'in', ('bank', 'cash'))])
    journal_id = fields.Many2one('account.journal', string="Journal", domain=[('type', '=', 'general')])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('waiting_approval_2', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('paid', 'Paid'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', copy=False, )

    def button_open_payments(self):
        ''' Redirect the user to this payment journal.
        :return:    An action on account.move.
        '''
        self.ensure_one()
        return {
            'name': _("Payments"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'form',
            'res_id': self.payment_move_id.id,
        }

    def button_open_journal_entry(self):
        ''' Redirect the user to this payment journal.
        :return:    An action on account.move.
        '''
        self.ensure_one()
        return {
            'name': _("Journal Entry"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'form',
            'res_id': self.account_move_id.id,
        }

    # def action_register_payment(self):
    #     ''' Open the account.payment.register wizard to pay the selected journal entries.
    #     :return: An action opening the account.payment.register wizard.
    #     '''
    #     vals = {
    #             'active_model': 'account.move',
    #             'active_ids': self.account_move_id.ids,
    #             'default_payment_type': 'outbound',
    #             'default_journal_id': self.treasury_journal_id.id,
    #             'default_amount': self.loan_amount,
    #         }
    #     return {
    #         'name': _('Register Payment'),
    #         'res_model': 'account.payment.register',
    #         'view_mode': 'form',
    #         'context': vals,
    #         'target': 'new',
    #         'type': 'ir.actions.act_window',
    #     }
    def _get_partner_id(self):
        for ptt in self:
            partner_id = False
            if ptt.employee_id.address_home_id:
                partner_id = ptt.employee_id.address_home_id.id
                # print("llll",ptt.employee_id.address_home_id.name)
            elif ptt.employee_id.user_id:
                partner_id = ptt.employee_id.user_id.partner_id.id
                # print("kkk",ptt.employee_id.user_id.partner_id.name)

            return partner_id

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
                credit_account_id = loan.employee_id.address_home_id.property_account_payable_id.id

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
                loan.account_move_id = move.id
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
            credit_account_id = loan.employee_id.address_home_id.property_account_payable_id.id

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
            loan.account_move_id = move.id
            move.post()
        self.write({'state': 'approve'})
        return True

    def action_register_loan_payment(self):
        for loan in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = loan.payment_date
            name = _('loan Cash of %s') % (loan.employee_id.name)
            pay_journal = loan.treasury_journal_id
            move_dict = {
                'narration': name,
                'ref': loan.name,
                'journal_id': pay_journal.id,
                'date': date,
            }
            precision = self.env['decimal.precision'].precision_get('Account')
            amount = loan.loan_amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            partner_id = loan._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    loan.employee_id.name))

            debit_account_id = loan.employee_id.address_home_id.property_account_payable_id.id

            # credit_account_id = loan.pay_journal_id.default_account_id.id

            pay_account_id = loan.treasury_journal_id.outbound_payment_method_line_ids.mapped('payment_account_id')
            if pay_account_id:
                credit_account_id = pay_account_id.id
            else:
                credit_account_id = self.company_id.account_journal_payment_credit_account_id.id

            # create payment
            # journal_currency = pay_journal.currency_id or pay_journal.company_id.currency_id
           
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': loan.name,
                    'partner_id': partner_id,
                    'account_id': debit_account_id,
                    'journal_id': pay_journal.id,
                    'loan_id': loan.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': loan.name,
                    'partner_id': partner_id,
                    'account_id': credit_account_id,
                    'journal_id': pay_journal.id,
                    'loan_id': loan.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
            # print('line ids is', line_ids)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            # move.loan_move_id = loan.id
            loan.write({'payment_move_id': move.id})
            move.post()
        # self.send_paid_email_to_loan_cash_employee()
        self.write({'state': 'paid'})
        return True
