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

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class PettyReamountWizard(models.TransientModel):
    _name = 'petty.reamount.wizard'

    petty_id = fields.Many2one('petty.cash', 'Petty Cash',required="1")
    journal_id = fields.Many2one('account.journal', string='Payment Jouranl',required="1")
    payment_date = fields.Date(required=1)
    diffrence = fields.Float()

    def action_reamount(self):
        for rec in self:
            rec.action_register_petty_payment()
            


    def action_register_petty_payment(self):
        for rec in self:

            petty = rec.petty_id

            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = rec.payment_date
            name = _('Petty Cash of %s') % (petty.employee_id.name)
            pay_journal = rec.journal_id
            move_dict = {
                'narration': name,
                'ref': petty.name,
                'journal_id': petty.pay_journal_id.id,
                'date': date,
                'petty_id':False
            }
            precision = self.env['decimal.precision'].precision_get('Account')
            amount = rec.diffrence
            if float_is_zero(amount, precision_digits=precision):
                continue
            partner_id = petty._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    petty.employee_id.name))
            debit_account_id = petty.journal_id.default_account_id.id
            credit_account_id = rec.journal_id.default_account_id.id

            # create payment
            # payment_methods = (amount < 0) and pay_journal.outbound_payment_method_ids or pay_journal.inbound_payment_method_ids
            journal_currency = pay_journal.currency_id or pay_journal.company_id.currency_id
            
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': debit_account_id,
                    'journal_id': pay_journal.id,
                    'petty_id': petty.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': credit_account_id,
                    'journal_id': pay_journal.id,
                    'petty_id': petty.id,
                    
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
            # print('line ids is', line_ids)
            move_dict['line_ids'] = line_ids
            
            move = self.env['account.move'].create(move_dict)
            # for line in move.line_ids:
            #     line.petty_id = petty.id
            move.petty_move_id = petty.id
            # petty.write({'account_move_id': move.id})
            
            move.post()
            self.env['petty.cash.line'].create({
            'name': 'Reamount',
            'amount': abs(amount)*-1,
            'petty_id': petty.id

        })
            petty._get_employee_balance2()
        # self.send_paid_email_to_petty_cash_employee()
        # self.write({'state': 'paid'})
        return True
class PettyPayWizard(models.TransientModel):
    _name = 'petty.pay.wizard'

    petty_id = fields.Many2one('petty.cash', 'Petty Cash')
    journal_id = fields.Many2one('account.journal', string='Payment Method',related='petty_id.journal_id',readonly=True)
    expense_sheet_id = fields.Many2one(comodel_name='hr.expense.sheet', string='Expense Sheet')
    partner_id = fields.Many2one('res.partner', string='Partner')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
                                         help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")


    balance = fields.Monetary(string='Balance', related='petty_id.balance')
    communication = fields.Char(string='Memo')

     
    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        if not self.journal_id:
            self.hide_payment_method = True
            return
        journal_payment_methods = self.journal_id.outbound_payment_method_ids
        self.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            return {
                'domain': {'payment_method_id': [('payment_type', '=', 'outbound'), ('id', 'in', payment_methods.ids)]}}
        return {}



    @api.onchange('employee_id')
    def onchange_employee_id(self):
        return {'domain': {'petty_id': [('employee_id', '=', self.employee_id.id)]}}


    def action_post(self):
        for pay in self:
            if pay.amount> pay.balance:
                raise ValidationError(_('You Cannot Exceed Employee Balance '))
            if pay.expense_sheet_id:
                expense_id = pay.expense_sheet_id
                domain = [('partner_id', '=', pay.partner_id.id),('move_id','=',expense_id.account_move_id.id),
                          ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                          ('amount_residual_currency', '!=', 0.0)]
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                lines = self.env['account.move.line'].search(domain)
                # print('lines is', lines)
                petty=self.petty_id
                petty.register_payment(lines)
                self.env['petty.cash.line'].create({
                    'name':expense_id.name,
                    'amount':pay.amount,
                    'petty_id':petty.id

                })

    def _get_payment_vals(self):
        expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)
        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': self.partner_id.id,
            'journal_id': self.petty_id.journal_id.id,
            'company_id': self.petty_id.journal_id.company_id.id,
            'payment_method_id': self.payment_method_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            # 'branch_id': expense_sheet.branch_id.id,
            # 'communication': self.communication
        }

     
    def petty_expense_post_payment(self):
        self.ensure_one()
        if self.amount > self.balance:
            raise ValidationError(_('You Cannot Exceed Employee Balance '))
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        # print("//////////////////",active_ids,context)
        expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)
        # print('exp sheets is',expense_sheet,expense_sheet.name)

        # Create payment and post it
        # print('the payment vals is',self._get_payment_vals())
        payment = self.env['account.payment'].create(self._get_payment_vals())
        print("dddddddd",payment)
        print("dddddddd",payment.name)
        payment.post()
        # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
        account_move_lines_to_reconcile = self.env['account.move.line']
        payment.move_line_ids.sudo().write({'petty_id':self.petty_id.id})
        payment.move_id.sudo().write({'petty_id':self.petty_id.id})
        for line in payment.move_line_ids + expense_sheet.account_move_id.line_ids:
            if line.account_id.internal_type == 'payable':
                # print('account line reconicile state',line.name,line.reconciled)
                account_move_lines_to_reconcile |= line
        # print('moves to reconcile is',account_move_lines_to_reconcile)
        account_move_lines_to_reconcile.reconcile()
        self.env['petty.cash.line'].create({
            'name': expense_sheet.name,
            'amount': payment.amount,
            'petty_id': self.petty_id.id

        })

        return {'type': 'ir.actions.act_window_close'}



















































class PettyPayInvoiceWizard(models.TransientModel):
    _name = 'petty.pay.invoice.wizard'

    petty_id = fields.Many2one('petty.cash', 'Petty Cash')
    journal_id = fields.Many2one('account.journal', string='Payment Method',related='petty_id.journal_id',readonly=True)
    invoice_id = fields.Many2one(comodel_name='account.move', string='Invoice')
    partner_id = fields.Many2one('res.partner', string='Partner')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
                                         help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")


    balance = fields.Monetary(string='Balance', related='petty_id.balance')
    communication = fields.Char(string='Memo')

     
    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        if not self.journal_id:
            self.hide_payment_method = True
            return
        journal_payment_methods = self.journal_id.outbound_payment_method_ids
        self.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            return {
                'domain': {'payment_method_id': [('payment_type', '=', 'outbound'), ('id', 'in', payment_methods.ids)]}}
        return {}

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        return {'domain': {'petty_id': [('employee_id', '=', self.employee_id.id)]}}




    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     employee_id=False
    #     if self.partner_id:
    #         employee_ids=self.env['hr.employee'].search([('address_home_id','=',self.partner_id.id)])
    #         if employee_ids:
    #             employee_id=employee_ids[0].id
    #
    #     return {'domain': {'petty_id': [('employee_id', '=', employee_id)]}}

    def _get_payment_vals(self):
        return {
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'partner_id': self.partner_id.id,
            'journal_id': self.petty_id.journal_id.id,
            'company_id': self.petty_id.journal_id.company_id.id,
            'payment_method_id': self.payment_method_id.id,
            'amount': self.amount,
            # 'invoice_ids': [(4, self.invoice_id.id, None)],
            'currency_id': self.currency_id.id,
            # 'payment_date': self.payment_date,
            # 'communication': self.communication
        }

     
    def petty_invoice_post_payment(self):
        self.ensure_one()
        if self.amount > self.balance:
            raise ValidationError(_('You Cannot Exceed Employee Balance '))
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        invoice = self.invoice_id
        print('invoiceinvoiceinvoice',invoice)
        # print('invoice is is',invoice.state,invoice.name)

        # Create payment and post it
        # print('the payment vals is',self._get_payment_vals())

        payment = self.env['account.payment'].create(self._get_payment_vals())
        # print('mahmoud',payment)
        # reconciled_bill_ids=
        payment.post()
        payment.move_line_ids.sudo().write({'petty_id':self.petty_id.id})
        self.env['petty.cash.line'].create({
            'name': invoice.name,
            'amount': payment.amount,
            'petty_id': self.petty_id.id

        })

        return {'type': 'ir.actions.act_window_close'}



