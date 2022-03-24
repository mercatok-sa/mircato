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


class InvoicePettyPayWizard(models.TransientModel):
    _name = 'invoice.petty.pay.wizard'

    amount = fields.Monetary(string='Amount')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    journal_id = fields.Many2one('account.journal', string='Petty Journal', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id,
                                  required=True)
    invoice_id = fields.Many2one('account.move')
    date = fields.Date(string="Date", required=True, default=date.today(), )
    memo = fields.Char(string="Memo", required=False, )

    def create_petty_cash(self):
        if not self.amount:
            raise ValidationError(_('Please Select Amount'))
        if self.amount > self.invoice_id.amount_total:
            raise ValidationError(_('Please Select Amount <= Invoice Amount'))

        conf = self.env['ir.config_parameter'].sudo()
        petty_cash_type_id = int(conf.get_param('petty_cash_type_id'))
        if not petty_cash_type_id:
            raise UserError('Please configure Petty Cash Type In Sale/Settings')
        petty_cash_type_id = self.env['petty.cash.type'].browse(petty_cash_type_id)
        journal_id = self.journal_id
        petty_obj = self.env['petty.cash']

        vals = {
            'type_id': petty_cash_type_id.id,
            'state': 'draft',
            'journal_id': journal_id.id,
            'pay_journal_id': journal_id.id,
            'payment_date': self.date,
            'adj_date': petty_cash_type_id.adj_date if petty_cash_type_id.adj_date else fields.date.today() + relativedelta(
                months=5),
            'employee_id': self.employee_id.id,
            'amount': self.amount,
            'inv_ref': self.invoice_id.name
        }
        petty_id = petty_obj.create(vals)
        petty_id.action_approve()

        # TODO Petty Cash Payment
        line_ids = []
        date = petty_id.payment_date
        name = _('Petty Cash of %s') % (petty_id.employee_id.name)
        pay_journal = petty_id.journal_id
        move_dict = {
            'narration': name,
            'ref': petty_id.name,
            'journal_id': petty_id.journal_id.id,
            'date': date,
        }
        # precision = self.env['decimal.precision'].precision_get('Account')
        amount = petty_id.amount
        partner_id = self.invoice_id.partner_id
        debit_account_id = petty_id.journal_id.default_account_id.id
        credit_account_id = partner_id.property_account_receivable_id.id
        if debit_account_id:
            debit_line = (0, 0, {
                'name': petty_id.name,
                'partner_id': partner_id.id,
                'account_id': debit_account_id,
                'journal_id': pay_journal.id,
                'petty_id': petty_id.id,
                'date': date,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
            })
            line_ids.append(debit_line)

        if credit_account_id:
            credit_line = (0, 0, {
                'name': petty_id.name,
                'partner_id': partner_id.id,
                'account_id': credit_account_id,
                'journal_id': pay_journal.id,
                'petty_id': petty_id.id,
                'date': date,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
            })
            line_ids.append(credit_line)
        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        petty_id.write({'account_move_id': move.id})
        petty_id.write({'state': 'paid'})
        move.post()

        inv_moves = self.invoice_id.move_id
        petty_moves = petty_id.account_move_id
        account_move_lines_to_reconcile = self.env['account.move.line']
        for line in inv_moves.line_ids + petty_moves.line_ids:
            if line.account_id.internal_type == 'receivable' and line.reconciled == False:
                account_move_lines_to_reconcile |= line

        account_move_lines_to_reconcile.reconcile()
