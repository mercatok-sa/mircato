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
from odoo import models, fields, api, tools, _
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

import time
import babel
import math


class PettyPayWizard(models.TransientModel):
    _inherit = 'petty.pay.wizard'

    total_balance = fields.Monetary(string='Total Balance', compute='_get_total_balance')
    petty_id = fields.Many2many('petty.cash', string='Petty Cash')
    balance = fields.Monetary(string='Balance', compute="_calc_balance", related=False)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            pets = self.env['petty.cash'].search([('employee_id', '=', self.employee_id.id), ('balance', '>', 0.0)])
            petty_list = []
            for rec in pets:
                if rec.balance > 0.0:
                    petty_list.append(rec.id)
            if pets:
                return {
                    'domain': {'petty_id': [('id', 'in', petty_list)]}}

            else:
                return {
                    'domain': {'petty_id': [('id', '=', [])]}}
        else:
            return {
                'domain': {'petty_id': [('id', '=', [])]}}

    @api.depends('petty_id')
    def _calc_balance(self):
        for line in self:
            total_balance = 0.0
            for petty in line.petty_id:
                total_balance += petty.balance
            line.balance = total_balance

     
    @api.depends('employee_id')
    def _get_total_balance(self):
        for rec in self:
            if rec.employee_id:
                res = self.env['petty.cash'].search([('employee_id', '=', rec.employee_id.id)])
                if res:
                    rec.total_balance = sum(x.balance for x in res)
                else:
                    rec.total_balance = 0.00
            else:
                    rec.total_balance = 0.00

    def _get_payment_vals(self, petty_id, amount):
        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': self.partner_id.id,
            'journal_id': petty_id.journal_id.id,
            'company_id': petty_id.journal_id.company_id.id,
            'payment_method_id': self.payment_method_id.id,
            'amount': amount,
            'currency_id': self.currency_id.id,
            'expens_id': self.expense_sheet_id.id
            # 'payment_date': self.payment_date,
            # 'communication': self.communication
        }

     
    def petty_expense_post_payment(self):
        self.ensure_one()
        # if self.amount > self.balance:
        #     raise ValidationError(_('You Cannot Exceed Employee Balance '))
        # print("KO", self.env.context.get('expense_sheet'))
        exp_sheet_id = self.env.context.get('expense_sheet')
        expense_sheet = self.env['hr.expense.sheet'].browse(exp_sheet_id)
        amount = self.amount
        for petty in self.petty_id:
            if amount > 0.0 and petty.balance > 0.0:
                if amount > petty.balance:
                    self.create_payment(petty, petty.balance, expense_sheet)
                    amount -= petty.balance
                else:
                    self.create_payment(petty, amount, expense_sheet)
                    amount = 0.0

        return {'type': 'ir.actions.act_window_close'}

    def create_payment(self, petty, amount, expense_sheet):
        payment = self.env['account.payment'].create(self._get_payment_vals(petty, amount))
        print('777777777777777777777777777777777777777777777777',payment.name)
        payment.name=False
        payment.action_post()
        print('888888888888888888888888888888888888888888888888888888',payment.name)
        # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
        account_move_lines_to_reconcile = self.env['account.move.line']
        # payment.invoice_line_ids.sudo().write({'petty_id': petty.id})
        payment.move_id.sudo().write({'petty_id': petty})
        for line in payment.invoice_line_ids + expense_sheet.account_move_id.line_ids:
            if line.account_id.internal_type == 'payable' and line.reconciled == False:
                account_move_lines_to_reconcile |= line
        # print("LLLL", account_move_lines_to_reconcile)
        account_move_lines_to_reconcile.reconcile()
        self.env['petty.cash.line'].create({
            'name': expense_sheet.name,
            'amount': payment.amount,
            'petty_id': petty.id

        })


class PettyPayInvoiceWizard(models.TransientModel):
    _inherit = 'petty.pay.invoice.wizard'


    petty_id = fields.Many2many('petty.cash', string='Petty Cash',)
    balance = fields.Monetary(string='Balance', compute="_calc_balance", related=False)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            pets = self.env['petty.cash'].search([('employee_id', '=', self.employee_id.id), ('balance', '>', 0.0)])
            petty_list = []
            for rec in pets:
                if rec.balance > 0.0:
                    petty_list.append(rec.id)
            # if pets:
            return {
                'domain': {'petty_id': [('id', 'in', petty_list)]}}
        return {}

    @api.depends('petty_id')
    def _calc_balance(self):
        for line in self:
            total_balance = 0.0
            for petty in line.petty_id:
                total_balance += petty.balance
            line.balance = total_balance

    def _get_payment_vals(self, amount, petty_id):

        data = {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': self.partner_id.id,
            'journal_id': petty_id.journal_id.id,
            'company_id': petty_id.journal_id.company_id.id,
            'payment_method_id': self.payment_method_id.id,
            'amount': amount,
            # 'invoice_ids': [(4, self.invoice_id.id, None)],
            'currency_id': self.currency_id.id,
            # 'payment_date': self.payment_date,
            # 'communication': self.communication
        }
        if self.invoice_id.move_type == 'out_invoice':
            data['partner_type'] = 'customer'
            data['payment_type'] = 'inbound'
        return data

     
    def petty_invoice_post_payment(self):
        self.ensure_one()
        # if self.amount > self.balance:
        #     raise ValidationError(_('You Cannot Exceed Employee Balance '))
        amount = self.amount
        for petty in self.petty_id:
            if amount > 0.0 and petty.balance > 0.0:
                if amount > petty.balance:
                    self.create_payment(petty, petty.balance)
                    amount -= petty.balance
                else:
                    self.create_payment(petty, amount)
                    amount = 0.0

        self = self.with_context(petty=True)
        return {'type': 'ir.actions.act_window_close'}

    def create_payment(self, petty, amount):
        
        # Create payment and post it
        payment = self.env['account.payment'].create(self._get_payment_vals(amount, petty))
        payment.action_post()
        payment.invoice_line_ids.sudo().write({'petty_id': petty.id})
        
        #link payment with bill or invoice automaticlly
        payment.move_id.sudo().write({'petty_id': petty})
        
        dest_line = payment.move_id.line_ids.filtered(lambda mv: mv.account_id.id == payment.destination_account_id.id)
        self.invoice_id.js_assign_outstanding_line(dest_line.id)
        self.invoice_id._compute_amount()
        
        
        self.env['petty.cash.line'].create({
            'name': self.invoice_id.name,
            'amount': payment.amount,
            'petty_id': petty.id
        })


class Payment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def create(self, vals):
        if self.env.context.get('petty'):
            new_record = super(Payment, self.with_context(active_id=self.env.context.get('default_invoice_id'),
                                                          active_ids=[
                                                              self.env.context.get('default_invoice_id')])).create(vals)
        else:
            new_record = super(Payment, self).create(vals)

        return new_record
