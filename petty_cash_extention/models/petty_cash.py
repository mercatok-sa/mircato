# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
class PettyCash(models.Model):
    _inherit = 'petty.cash'

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name+'/[ '+str(rec.balance) + ' ]'
            result.append((rec.id, name))
        return result
     
    def unlink(self):
        for line in self:
            if line.state == 'paid':
                raise exceptions.ValidationError('You Can not delete paid petty cash \n You can cancel it only !')
        res = super(PettyCash, self).unlink()
        return res
    def action_cancel(self):
        adj_id = self.env['petty.cash.adj'].create({
            'petty_id': self.id,
            'pay_journal_id': self.pay_journal_id.id,
            'payment_date': date.today(),
        })
        adj_id.action_approve()
        adj_id.action_register_petty_adj_payment()
        self.state = 'reconciled'

    # @api.model
    # def create(self, vals): #24-04-2021
    #     res =super(PettyCash, self).create(vals)
    #     recipient_partners = []
    #     if vals.get('employee_id'):

    #         user_obj = self.env['hr.employee'].search([('id','=',vals.get('employee_id'))])
    #         # if user_obj:
    #         #    recipient_partners.append(user_obj.user_id.partner_id.id)
    #         if user_obj and user_obj.parent_id and user_obj.parent_id.user_id and user_obj.parent_id.user_id.partner_id and user_obj.parent_id.user_id.partner_id.email:
    #             print("333333")
    #             # recipient_partners.append(user_obj.user_id.partner_id.id)
    #             recipient_partners.append(user_obj.parent_id.user_id.partner_id.id)
    #         # else:
    #         #     raise exceptiossns.ValidationError('Please configure Email for manager of this employee')
    #             post_vars = {'subject': "Notification About New Petty Cash Created ",
    #                          'body': '<h3>This is a notification about Petty Cash</h3> <p> '+str(res.name)+
    #                                      ' Is Submitted Kindly Review It</p><div><a href="/web?#id=' + str(
    #                                  res.id) + '&model=petty.cash&action=petty_cash_management.action_view_petty_cash'
    #                                            '" style="font-weight: bold">'+str(res.name)+'</a></div>',
    #                          'partner_ids': recipient_partners, }

    #             message = self.env['mail.thread'].message_post(message_type="notification",**post_vars)
    #             print(message)
    #     return res


     
    # def write(self, vals): #24-04-2021
    #     for rec in self:
    #         recipient_partners = []
    #         if vals.get('employee_id'):

    #             # user_obj = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])
    #             user_obj = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])
    #             if user_obj and user_obj.parent_id and user_obj.parent_id.user_id and  user_obj.parent_id.user_id.partner_id and  user_obj.parent_id.user_id.partner_id.email :
    #                 print("2222")

    #                 # recipient_partners.append(user_obj.user_id.partner_id.id)
    #                 recipient_partners.append(user_obj.parent_id.user_id.partner_id.id)
    #             # else:
    #             #     raise exceptions.ValidationError('Please configure Email for manager of this employee')
    #                 post_vars = {'subject': "Notification About New Petty Cash Created ",
    #                              'body': '<h3>This is a notification about Petty Cash</h3> <p> '+str(rec.name)+
    #                                      ' Is Submitted Kindly Review It</p><div><a href="/web?#id=' + str(
    #                                  rec.id) + '&model=petty.cash&action=petty_cash_management.action_view_petty_cash'
    #                                            '" style="font-weight: bold">'+str(rec.name)+'</a></div>',
    #                              'partner_ids': recipient_partners, }

    #                 message = self.env['mail.thread'].message_post(message_type="notification", **post_vars)
    #     return super(PettyCash, self).write(vals)
