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

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_petty_cash = fields.Boolean(string='')

class PettyCashType(models.Model):
    _name = 'petty.cash.type'

    _description = 'Petty Cash Types'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')], string='State',
        copy=False, default='draft')

    type = fields.Selection([
        ('temp', 'Temporary'),
        ('per', 'Permanent')], string='Type',
        copy=False, default='temp')

    name = fields.Char(
        'name', copy=False)
    journal_id = fields.Many2one(comodel_name='account.journal', string='Petty Cash Journal',domain="[('is_petty_cash', '=', True)]")
    reference = fields.Char('Reference')
    payment_date = fields.Date('Payment Date')
    adj_date = fields.Date('Adjustment Date')
    force_date = fields.Boolean('Force Adjustment Date')
    move_group = fields.Boolean('Group Journal Entries')

     
    def unlink(self):
        if self.env['petty.cash'].search([('type_id', 'in', self.ids)], limit=1):
            raise UserError(_('You cannot delete Petty Cash type that has been used in petty cash before'))
        return super(PettyCashType, self).unlink()

     
    def action_confirm(self):

        self.write({'state': 'confirm'})
        return True

     
    def action_draft(self):
        if self.env['petty.cash'].search([('type_id', 'in', self.ids)], limit=1):
            raise UserError(_('You cannot Set To Draft Petty Cash type that has been used in petty cash before'))
        self.write({'state': 'draft'})
        return True

#class CrossoveredBudget(models.Model):
#    _inherit = 'crossovered.budget'
#
#    analytic_account_id = fields.Many2one('account.analytic.account',)

class PettyCash(models.Model):
    _name = 'petty.cash'
    _description = 'Employees Petty Cash'
    _inherit = ['mail.thread']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),('refuse', 'Refused'),
        ('paid', 'Paid'), ('reconciled', 'Reconciled')], string='State',
        copy=False, default='draft')

    name = fields.Char(
        'Reference', copy=False, readonly=True, default=lambda x: _('New'))
    type_id = fields.Many2one(comodel_name='petty.cash.type', string='Petty Cash Type',
                              domain="[('state', '=', 'confirm')]")
    
    petty_type = fields.Selection(string='Type',
                                  copy=False,
                                  related="type_id.type",
                                  store=True)

    amount = fields.Monetary('Amount')
    account_move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)
    account_move_ids = fields.One2many('account.move','petty_move_id',)
    line_ids = fields.One2many(comodel_name='petty.cash.line', inverse_name='petty_id', string='Lines')

    remain_amount = fields.Monetary('Remaining Amount')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee To assign', required=True, default=lambda self: self.env.user.employee_id.id)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    payment_date = fields.Date('Payment Date',default=fields.Date.context_today)
    adj_date = fields.Date('Adjustment Date',)
    journal_id = fields.Many2one(comodel_name='account.journal', string='Petty Cash Journal',
    related='type_id.journal_id', store=True,) #domain=[('is_petty_cash','!=',True)])
    pay_journal_id = fields.Many2one(comodel_name='account.journal', string='Payment Journal',
                                     domain=[('type', 'in', ['cash', 'bank']),('is_petty_cash','!=',True)])
    reference = fields.Char('Reference')
    payment_ids = fields.Many2many(comodel_name='account.payment', string='Payments', copy=False)
    payment_count = fields.Integer(string='# of Payments', compute='_get_payment', readonly=True, copy=False)
    paid = fields.Boolean(string='Is Paid', compute='_compute_paid')
    balance = fields.Monetary('Balance', compute='_get_employee_balance2',store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    view_register_payment = fields.Char(compute='_compute_view_register_payment', string='')
    project_id = fields.Many2one('project.project', string='Project')
    analytic_account_id = fields.Many2one('account.analytic.account',
        string="Analytic Account", store=True,)

    def action_add_amount_petty_balance(self):
        for rec in self:
            
            view = self.env.ref('petty_cash_management.petty_reamount_wizard_from_view')
            ctx = dict(self.env.context or {})
            diffrecne = rec.amount - rec.balance
            if diffrecne == 0:
                raise ValidationError(_('Sorry , Diffrence Between Amount and Balance must be greater than Zero.'))
            
            ctx.update({
                # 'default_sale_id': petty.id,
                'default_petty_id': rec.id,
                'default_diffrence':diffrecne
            })
            # print('the ctx is',ctx)
            return {
                'name': _('Reamount '),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'petty.reamount.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }
    #def action_view_petty_cash_bugdet(self):
    #    self.ensure_one()
    #    return {
    #        'name': 'Project Budget',
    #        'type': 'ir.actions.act_window',
    #        'view_mode': 'tree',
    #        'res_model': 'crossovered.budget',
    #        # 'domain': [('analytic_account_id', '=', self.analytic_account_id.id)],
    #        # 'context': {'default_analytic_account_id': self.analytic_account_id.id , 'create': True,'write':True}
    #    }

    @api.model
    def send_paid_email_to_petty_cash_employee(self):
        template = self.env.ref('petty_cash_management.email_paid_to_petty_cash_employee')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    @api.model
    def send_refuse_email_to_petty_cash_employee(self):
        template = self.env.ref('petty_cash_management.email_refuse_to_petty_cash_employee')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    @api.model
    def send_approve_email_to_petty_cash_employee(self):
        template = self.env.ref('petty_cash_management.email_approve_to_petty_cash_employee')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    def _compute_view_register_payment(self):
        for rec in self:
            if self.env.user.has_group('petty_cash_management.group_petty_cash_accountant'): 
                rec.view_register_payment = True
            else:
                rec.view_register_payment = False

    def get_email_to_petty_cash_accountant(self):
        email_list = []
        user_group = self.env.ref("petty_cash_management.group_petty_cash_accountant")
        email_list = [usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def send_email_to_petty_cash_accountant(self):
        template = self.env.ref('petty_cash_management.email_to_register_petty_cash_accountant')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    def get_email_to_petty_cash_managers(self):
        email_list = []
        user_group = self.env.ref("petty_cash_management.group_petty_cash_manager")
        email_list = [usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def send_email_to_petty_cash_manager(self):
        template = self.env.ref('petty_cash_management.ask_to_approve_petty_cash_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    def register_payment(self, payment_line):
        line_to_reconcile = self.env['account.move.line']
        for petty in self:
            line_to_reconcile += petty.account_move_id.line_ids.filtered(
                lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
        # print('iam in petty register and lines is', line_to_reconcile, payment_line)
        return (line_to_reconcile + payment_line).reconcile()

    @api.constrains('amount')
    def _check_amount(self):
        for petty in self:
            if petty.amount <= 0:
                raise ValidationError(_('Petty cash amount must be more than 0'))

    @api.depends('line_ids','state')
    def _get_employee_balance2(self):
        account_move_line_obj = self.env['account.move.line']
        for petty in self:
            balance = 0.00
            partner_id = petty._get_partner_id()
            move_lines = account_move_line_obj.search([('partner_id', '=', partner_id),
                                                       ('account_id', 'in',
                                                        [petty.journal_id.default_account_id.id,
                                                         petty.journal_id.default_account_id.id]),
                                                       ('balance', '!=', 0),
                                                       ('petty_id', '=', petty.id)])
            if move_lines:
                balance = sum([m.balance for m in move_lines])
            paid = sum([l.amount for l in petty.line_ids])
            if petty.state == 'paid':
                # if balance != 0.00:
                #     petty.balance = balance
                # else:
                petty.balance = petty.amount - paid
            else:
                petty.balance = 0.0

     
    @api.depends('payment_ids')
    def _compute_paid(self):
        for petty in self:
            paid_amount = sum([p.amount for p in petty.payment_ids])
            # print('pai amount is', paid_amount)
            if paid_amount >= petty.amount:
                # print('the state will be paid')
                # petty.write({'state': 'paid'})
                petty.paid = True

     
    @api.depends('payment_ids')
    def _get_payment(self):
        for petty in self:
            petty.payment_count = len(petty.payment_ids.ids)
            paid_amount = sum([p.amount for p in petty.payment_ids])
            # print('pai amount is',paid_amount)
            # if paid_amount >=petty.amount:
            #     print('thestate will be paid')
            #     petty.write({'state':'paid'})

     
    def action_register_petty_payment2(self):
        # this method is from the petty cash journal and the employee payable account
        for petty in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = petty.payment_date
            name = _('Petty Cash of %s') % (petty.employee_id.name)
            move_dict = {
                'narration': name,
                'ref': petty.name,
                'journal_id': petty.journal_id.id,
                'date': date,
            }
            precision = self.env['decimal.precision'].precision_get('Account')
            amount = petty.amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            partner_id = petty._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    petty.employee_id.name))
            credit_account_id = petty.journal_id.default_account_id.id
            debit_account_id = petty.employee_id.address_home_id.property_account_payable_id.id

            # print('ammount is', amount)
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': debit_account_id,
                    'journal_id': petty.journal_id.id,
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
                    'journal_id': petty.journal_id.id,
                    'petty_id': petty.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
            # print('line ids is', line_ids)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            move.petty_move_id = petty.id
            petty.write({'account_move_id': move.id})
            move.post()
        self.write({'state': 'paid'})
        return True

     
    def action_register_petty_payment(self):
        for petty in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = petty.payment_date
            name = _('Petty Cash of %s') % (petty.employee_id.name)
            pay_journal = petty.pay_journal_id
            move_dict = {
                'narration': name,
                'ref': petty.name,
                'journal_id': petty.pay_journal_id.id,
                'date': date,
            }
            precision = self.env['decimal.precision'].precision_get('Account')
            amount = petty.amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            partner_id = petty._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    petty.employee_id.name))
            debit_account_id = petty.journal_id.default_account_id.id
            credit_account_id = petty.pay_journal_id.default_account_id.id

            # create payment
            # payment_methods = (amount < 0) and pay_journal.outbound_payment_method_ids or pay_journal.inbound_payment_method_ids
            journal_currency = pay_journal.currency_id or pay_journal.company_id.currency_id
            # payment = self.env['account.payment'].create({
            #     'payment_method_id': payment_methods and payment_methods[0].id or False,
            #     'payment_type': amount < 0 and 'outbound' or 'inbound',
            #     'partner_id': partner_id,
            #     'partner_type': 'supplier',
            #     'journal_id': pay_journal.id,
            #     'payment_date': date,
            #     'state': 'reconciled',
            #     'currency_id': journal_currency.id,
            #     'amount': abs(amount),
            #     'name': petty.name,
            # })
            # payment_id = payment.id

            # print('ammount is', amount)
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
                    # 'payment_id': payment_id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
            # print('line ids is', line_ids)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            move.petty_move_id = petty.id
            petty.write({'account_move_id': move.id})
            move.post()
        self.send_paid_email_to_petty_cash_employee()
        self.write({'state': 'paid'})
        return True

     
    def action_post(self):
        for petty in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = petty.payment_date
            name = _('Petty Cash of %s') % (petty.employee_id.name)
            move_dict = {
                'narration': name,
                'ref': petty.name,
                'journal_id': petty.journal_id.id,
                'date': date,
            }
            precision = self.env['decimal.precision'].precision_get('Account')
            amount = petty.amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            partner_id = petty._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    petty.employee_id.name))
            debit_account_id = petty.journal_id.default_account_id.id
            credit_account_id = petty.employee_id.address_home_id.property_account_payable_id.id
            # print('ammount is', amount)
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': debit_account_id,
                    'journal_id': petty.journal_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': petty.name,
                    'partner_id': partner_id,
                    'account_id': credit_account_id,
                    'journal_id': petty.journal_id.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            # print('line ids is', line_ids)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            move.petty_move_id = petty.id
            petty.write({'account_move_id': move.id})
            move.post()
        self.write({'state': 'post'})
        return True

    def action_refuse(self):
        self.send_refuse_email_to_petty_cash_employee()
        self.write({'state': 'refuse'})
        return True
     
    def action_approve(self):
        self.send_approve_email_to_petty_cash_employee()
        self.send_email_to_petty_cash_accountant()
        self.write({'state': 'approved'})
        return True
     
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

     
    def action_paid(self):
        return self.write({'state': 'paid'})

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            new_name = self.env['ir.sequence'].next_by_code('petty.cash') or _('New')
            values['name'] = new_name
        petty = super(PettyCash, self).create(values)
        return petty

    @api.onchange('type_id')
    def onchange_type(self):
        if self.type_id:
            # if self.type_id.journal_id.is_petty_cash != True:
            # if not self.journal_id:
            #     print('not self.journal_id')
            #     self.journal_id = self.type_id.journal_id
            self.adj_date = self.type_id.adj_date
            # else:
                # raise UserError(_('There is no petty cash journal related to this type.'))

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

     
    def action_view_payment(self):

        payments = self.mapped('payment_ids')
        action = self.env.ref('account.action_account_payments').read()[0]
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = payments.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def petty_register_payment(self):
        for petty in self:
            view = self.env.ref('petty_cash_management.view_account_payment_petty_cash_form')
            amount = petty.amount
            partner_id = petty._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    petty.employee_id.name))
            if petty.payment_ids:
                for pay in petty.payment_ids:
                    if pay.state == 'approved':
                        amount = amount - pay.amount

            context = "{'search_default_customer':1, 'show_address': 1}"
            ctx = dict(self.env.context or {})
            ctx.update({
                # 'default_sale_id': petty.id,
                'default_amount': amount,
                'default_communication': petty.name,
                'default_payment_type': 'outbound',
                'default_partner_type': 'supplier',
                'default_journal_id': petty.journal_id.id,
                'default_partner_id': partner_id,
                'default_petty_id': petty.id
            })
            return {
                'name': _('Add Payment To Petty Cash'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                # 'res_id': payment.id,
                'context': ctx,
            }


class PettyCashLine(models.Model):
    _name = 'petty.cash.line'

    name = fields.Char('Reference')
    amount = fields.Monetary('Amount')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    petty_id = fields.Many2one(comodel_name='petty.cash', string='Petty Cash')


class PettyCashAdjustment(models.Model):
    _name = 'petty.cash.adj'
    _description = 'Employees Petty Cash Adjustment'
    _inherit = ['mail.thread']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid'), ('reconciled', 'Reconciled')], string='State',
        copy=False, default='draft')

    name = fields.Char(
        'Reference', copy=False, readonly=True, default=lambda x: _('New'))

    petty_id = fields.Many2one(comodel_name='petty.cash', string='Petty Cash')
    type_id = fields.Many2one(related='petty_id.type_id', string='Petty Cash Type', store=True, readonly=1)
    journal_id = fields.Many2one(comodel_name='account.journal', related='petty_id.journal_id', store=True,
                                 readonly=True, string='Petty Cash Journal')
    pay_journal_id = fields.Many2one(comodel_name='account.journal', string='Payment Journal',
                                     domain=[('type', 'in', ['cash', 'bank']),])
    amount = fields.Monetary('Amount', compute='compute_amount')
    remain_amount = fields.Monetary('Remaining Amount')
    payment_date = fields.Date('Payment Date')
    account_move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)

    adj_date = fields.Date('Adjustment Date')
    employee_id = fields.Many2one(comodel_name='hr.employee', related='petty_id.employee_id', store=True, readonly=True,
                                  string='Employee To assign')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    @api.depends('type_id.type')
    def compute_amount(self):
        for adj in self:
            # print('iam in compute amount')
            if adj.type_id:
                if adj.type_id.type == 'temp':
                    adj.amount = -adj.petty_id.balance
                if adj.type_id.type == 'per':
                    adj.amount = adj.petty_id.amount - adj.petty_id.balance
            else:
                adj.amount = False

     
    def action_approve(self):
        self.write({'state': 'approved'})
        return True

     
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

     
    def action_paid(self):
        return self.write({'state': 'paid'})

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            new_name = self.env['ir.sequence'].next_by_code('petty.cash.adj') or _('New')
            values['name'] = new_name
        petty = super(PettyCashAdjustment, self).create(values)
        return petty

    def _get_partner_id(self):
        for ptt in self:
            partner_id = False
            if ptt.employee_id.address_home_id:
                partner_id = ptt.employee_id.address_home_id.id
            elif ptt.employee_id.user_id:
                partner_id = ptt.employee_id.user_id.partner_id.id
            return partner_id

     
    def action_register_petty_adj_payment(self):
        for adj in self:
            line_ids = []
            date = adj.payment_date
            name = _('Petty Cash Adjustment of %s') % (adj.petty_id.name)
            pay_journal = adj.pay_journal_id
            move_dict = {
                'narration': name,
                'ref': adj.name,
                'journal_id': adj.pay_journal_id.id,
                'date': date,
            }
            precision = self.env['decimal.precision'].precision_get('Account')
            amount = adj.amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            partner_id = adj._get_partner_id()
            if not partner_id:
                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (
                    adj.employee_id.name))
            debit_account_id = adj.journal_id.default_account_id.id
            credit_account_id = adj.pay_journal_id.default_account_id.id

            # create payment
            # payment_methods = (amount < 0) and pay_journal.outbound_payment_method_ids or pay_journal.inbound_payment_method_ids
            # print('ammount is', amount)
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': adj.name,
                    'partner_id': partner_id,
                    'account_id': debit_account_id,
                    'journal_id': pay_journal.id,
                    'petty_id': adj.petty_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
            if credit_account_id:
                credit_line = (0, 0, {
                    'name': adj.name,
                    'partner_id': partner_id,
                    'account_id': credit_account_id,
                    'journal_id': pay_journal.id,
                    'petty_id': adj.petty_id.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
            # print('line ids is', line_ids)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            account_move_lines_to_reconcile = self.env['account.move.line']
            # for line in move.line_ids + adj.petty_id.account_move_id.line_ids:
            #     if line.account_id.internal_type == 'payable':
            #         print('account line reconicile state', line.name, line.reconciled)
            #         account_move_lines_to_reconcile |= line
            # print('moves to reconcile is', account_move_lines_to_reconcile)
            # account_move_lines_to_reconcile.reconcile()
            adj.write({'account_move_id': move.id})
            move.post()
            self.env['petty.cash.line'].create({
            'name': adj.name,
            'amount': abs(amount),
            'petty_id': adj.petty_id.id

            })
        self.write({'state': 'paid'})
        return True
