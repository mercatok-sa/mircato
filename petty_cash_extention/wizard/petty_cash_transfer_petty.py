# -*- coding: utf-8 -*-

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


class PettyPCashTransfer(models.TransientModel):
    _name = 'petty.cash.transfer.petty'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    petty_id = fields.Many2one('petty.cash', string='Petty Cash')
    balance = fields.Monetary(string='Balance', related='petty_id.balance' )
    
    
    employee_trans_id = fields.Many2one('hr.employee', string=' Employee', required=True)
    petty_trans_id = fields.Many2one('petty.cash', string=' Petty Cash')
    balance_trans = fields.Monetary(string='Balance', related='petty_trans_id.balance' )

    amount = fields.Monetary(string='Amount')


    currency_id = fields.Many2one('res.currency',default=lambda self:self.env.user.company_id.currency_id.id)
    journal_id = fields.Many2one('account.journal','Journal')
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.petty_id=False
        if self.employee_id:
            pets = self.env['petty.cash'].search([('employee_id', '=', self.employee_id.id), ('balance', '>', 0.0)])
            petty_list=[]
            for rec in pets:
                if rec.balance>0.0:
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

    
    @api.onchange('employee_trans_id')
    def _onchange_employee_trans_id(self):
        self.petty_trans_id=False
        if self.employee_trans_id:
            pets = self.env['petty.cash'].search([('employee_id', '=', self.employee_trans_id.id)])
            petty_list=[]
            for rec in pets:
                #if rec.balance>0.0:
                petty_list.append(rec.id)
            if pets:
                return {
                    'domain': {'petty_trans_id': [('id', 'in', petty_list)]}}

            else:
                return {
                    'domain': {'petty_trans_id': [('id', '=', [])]}}
        else:
            return {
                'domain': {'petty_trans_id': [('id', '=', [])]}}



    def action_transfer(self):
        for rec in self:
            if rec.amount<=0:
                raise UserError('Please Select Amount')
            if rec.amount>rec.balance:
                raise UserError('Selected Amount must be <= Petty Cash Balance')
            if (rec.balance_trans + rec.amount) > rec.petty_trans_id.amount:
                raise UserError('Sorry!! , Transfere Amount+Balance must be less than Amount of Transfering Petty ')
            amount = rec.amount
            reference = rec.petty_id.name

            debit_vals = {
                'name': rec.petty_trans_id.name,
                # 'account_id': rec.journal_id.default_account_id.id,
                'account_id':rec.petty_trans_id.journal_id.default_account_id.id,
                'journal_id': rec.petty_trans_id.journal_id.id,
                'date': fields.date.today(),
                'debit': abs(amount),
                'credit': 0.0,
                'petty_id': rec.petty_trans_id.id,
                'partner_id': rec.petty_trans_id.employee_id.address_home_id.id,

            }
            credit_vals = {
                'name': rec.petty_id.name,
                'account_id': rec.petty_id.journal_id.default_account_id.id,
                'journal_id': rec.petty_id.journal_id.id,
                'date': fields.date.today(),
                'debit': 0.0,
                'credit': abs(amount),
                'petty_id': rec.petty_id.id,
                'partner_id': rec.petty_id.employee_id.address_home_id.id,

            }
            vals = {
                'ref': reference,
                # 'journal_id': rec.journal_id.id,
                'journal_id':rec.petty_trans_id.journal_id.id,
                'date': fields.date.today(),
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.post()
            self.env['petty.cash.line'].create({
                'name': 'Petty Transfer To: '+str(rec.petty_trans_id.name),
                'amount': rec.amount,
                'petty_id': rec.petty_id.id,


            })

            self.env['petty.cash.line'].create({
                'name': 'Petty Receive From: '+str(rec.petty_id.name),
                'amount': abs(rec.amount)*-1,
                'petty_id': rec.petty_trans_id.id,


            })

