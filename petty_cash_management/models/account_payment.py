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



class account_payment(models.Model):
    _inherit = "account.payment"

    petty_id=fields.Many2one('petty.cash','Petty Cash')




    #  
    # def post(self):
    #     res=super(account_payment,self).post()
    #     for pay in self:
    #         print('iam in ne wpost', res, pay.move_line_ids)
    #
    #         if pay.petty_id:
    #             pay.move_line_ids.sudo().write({'petty_id':pay.petty_id.ids})
    #             pay.petty_id.sudo().write({
    #                 'payment_ids':[(4,pay.id)]
    #             })
    #     return res



