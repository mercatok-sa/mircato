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
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def get_emp(self):
        emp_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return emp_id.id

    employee_id = fields.Many2one('hr.employee', 'Employee',) #default=get_emp)
    show_emps_petty_cashes = fields.Boolean(compute='get_show_emps_petty')

     
    @api.depends('show_emps_petty_cashes')
    def get_show_emps_petty(self):
        for rec in self:
            rec.show_emps_petty_cashes = self.env.user.show_emps_petty_cashes

    def petty_inv_pay(self):

        flag = True
        for inv in self:

            view = self.env.ref('petty_cash_management.petty_pay_invoice_wizard_from_view')
            # amount = inv.amount_total
            amount = inv.amount_residual
            partner_id = inv.partner_id.id
            if not inv.employee_id:
                raise ValidationError(_('Please Select Employee...'))

            # raise ValidationError(_('Partner Has no relate Employee'))
            ctx = dict(self.env.context or {})
            ctx.update({
                'default_employee_id': inv.employee_id.id,
                'default_amount': amount,
                'default_invoice_id': inv.id,
                'default_currency_id': inv.currency_id.id,
                'default_partner_id': partner_id,

                'flag': True if flag else False
            })

            # print('the ctx is', ctx)
            return {
                'name': _('Pay With Petty Cash'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'petty.pay.invoice.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,

            }

    def create_customer_inv_petty_cash(self):
        emp_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return {
            'name': _('Create Petty Cash'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'invoice.petty.pay.wizard',
            'target': 'new',
            # 'res_id': payment.id,
            'context': {
                'default_invoice_id': self.id,
                # 'default_amount': self.residual,
                'default_amount': self.amount_total,
                'default_employee_id': emp_id.id or False
            },
        }


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def petty_pay(self):
        res = super(HrExpenseSheet, self).petty_pay()
        # print("IIIIIIIIIIIIIIIIII")
        if res.get('context'):
            ctx = res.get('context')
            payment_obj = self.env['account.payment'].search([('expens_id', '=', self.id)])
            if payment_obj:
                payment_amt = sum(x.amount for x in payment_obj)
            else:
                payment_amt = 0
            ctx.update({'default_amount': ctx.get('default_amount') - payment_amt})
            res.update({'context': ctx})
            # print(payment_amt)
            # print (amount)
            # print(res)
        return res


class Payment(models.Model):
    _inherit = 'account.payment'

    expens_id = fields.Many2one(comodel_name="hr.expense.sheet", string="Expense", required=False, )
