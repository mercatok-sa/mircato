# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime


class PettyCash(models.Model):
    _inherit = 'petty.cash'

    origin = fields.Char('Origin')
    inv_ref = fields.Char('Invoice Ref')
    is_empty = fields.Boolean(string="Empty", )
    notes = fields.Text(string="Notes", required=False, )
    #  
    # @api.depends('balance')
    # def calc_petty_empty(self):
    #     if self.balance <= 0.0:
    #         self.is_empty = True

     
    # def get_employee_balance2(self):
    #     account_move_line_obj = self.env['account.move.line']
    #     for petty in self:
    #         balance = 0
    #         move_lines = account_move_line_obj.search([
    #             ('account_id', 'in',
    #              [petty.journal_id.default_account_id.id,
    #               petty.journal_id.default_account_id.id]),
    #             ('balance', '!=', 0.0),
    #             ('petty_id', '=', petty.id)])
    #         if move_lines:
    #             balance = sum([m.balance for m in move_lines])
    #         paid = sum([l.amount for l in petty.line_ids])
    #         petty.balance = balance
