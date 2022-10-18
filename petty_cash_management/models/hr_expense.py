# -*- coding: utf-8 -*-

##############################################################################
#
#
#    Copyright (C) 2018-TODAY .
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrExpenseSheet(models.Model):

    _inherit= "hr.expense.sheet"

    # branch_id = fields.Many2one(comodel_name="res.branch", string="Branch",)

     
    # def action_move_create(self):
    #     '''
    #     main function that is called when trying to create the accounting entries related to an expense
    #     '''
    #     move_group_by_sheet = self._get_account_move_by_sheet()
    #
    #     move_line_values_by_expense = self._get_account_move_line_values()
    #
    #     for expense in self:
    #         company_currency = expense.company_id.currency_id
    #         different_currency = expense.currency_id != company_currency
    #
    #         # get the account move of the related sheet
    #         move = move_group_by_sheet[expense.sheet_id.id]
    #
    #         # get move line values
    #         move_line_values = move_line_values_by_expense.get(expense.id)
    #         move_line_dst = move_line_values[-1]
    #         total_amount = move_line_dst['debit'] or -move_line_dst['credit']
    #         total_amount_currency = move_line_dst['amount_currency']
    #
    #         # create one more move line, a counterline for the total on payable account
    #         if expense.payment_mode == 'company_account':
    #             if not expense.sheet_id.bank_journal_id.default_account_id:
    #                 raise UserError(_("No credit account found for the %s journal, please configure one.") % (
    #                     expense.sheet_id.bank_journal_id.name))
    #             journal = expense.sheet_id.bank_journal_id
    #             # create payment
    #             payment_methods = journal.outbound_payment_method_ids if total_amount < 0 else journal.inbound_payment_method_ids
    #             journal_currency = journal.currency_id or journal.company_id.currency_id
    #             payment = self.env['account.payment'].create({
    #                 'payment_method_id': payment_methods and payment_methods[0].id or False,
    #                 'payment_type': 'outbound' if total_amount < 0 else 'inbound',
    #                 'partner_id': expense.employee_id.address_home_id.commercial_partner_id.id,
    #                 'partner_type': 'supplier',
    #                 'journal_id': journal.id,
    #                 'payment_date': expense.date,
    #                 'state': 'reconciled',
    #                 'currency_id': expense.currency_id.id if different_currency else journal_currency.id,
    #                 'amount': abs(total_amount_currency) if different_currency else abs(total_amount),
    #                 # 'name': expense.name,
    #             })
    #             print('paymentpayment',payment)
    #             move_line_dst['payment_id'] = payment.id
    #
    #         # link move lines to move, and move to expense sheet
    #         move.with_context(dont_create_taxes=True).write({
    #             'line_ids': [(0, 0, line) for line in move_line_values]
    #         })
    #         expense.sheet_id.write({'account_move_id': move.id})
    #
    #         if expense.payment_mode == 'company_account':
    #             expense.sheet_id.paid_expense_sheets()
    #
    #     # post the moves
    #     for move in move_group_by_sheet.values():
    #         move.post()
    #
    #     return move_group_by_sheet

    def petty_pay(self):
        for exp in self:
            view = self.env.ref('petty_cash_management.petty_pay_wizard_from_view')
            amount = exp.total_amount
            partner_id = self.employee_id.address_home_id.commercial_partner_id.id
            petty_cash_ids=self.env['petty.cash'].search([('employee_id','=',exp.employee_id.id),('state','=','paid')])
            # print('petty cash ids is',petty_cash_ids)
            if not partner_id:

                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    exp.employee_id.name))
            ctx = dict(self.env.context or {})
            ctx.update({
                # 'default_sale_id': petty.id,
                'default_employee_id': exp.employee_id.id,
                'default_amount': amount,
                'default_expense_sheet_id': exp.id,
                'default_currency_id':exp.currency_id.id,
                'default_partner_id': partner_id,
            })
            return {
                'name': _('Add Payment To Petty Cash'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'petty.pay.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }

