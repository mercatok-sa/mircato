# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
class Sale(models.TransientModel):
    _inherit = 'res.config.settings'

    petty_cash_type_id = fields.Many2one('petty.cash.type','Petty Cash Type')
    # pay_journal_id = fields.Many2one('account.journal','Payment Journal')

     
    def get_values(self):
        res = super(Sale, self).get_values()
        conf = self.env['ir.config_parameter'].sudo()
        res.update(
            # pay_journal_id=int(conf.get_param('pay_journal_id')),
            petty_cash_type_id=int(conf.get_param('petty_cash_type_id')),

        )
        return res

     
    def set_values(self):
        obj = self.env['ir.config_parameter'].sudo()
        # obj.set_param('pay_journal_id', int(self.pay_journal_id.id))
        obj.set_param('petty_cash_type_id', int(self.petty_cash_type_id.id))
        super(Sale, self).set_values()
