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

     
    def petty_expense_post_payment(self):
        res = super(PettyPayWizard, self.with_context(active_id=self.env.context.get('default_expense_sheet_id'),
                                                      active_ids=[self.env.context.get(
                                                          'default_expense_sheet_id')])).petty_expense_post_payment()
        active_id = self.env.context.get('default_expense_sheet_id')
        expense_sheet = self.env['hr.expense.sheet'].browse(active_id)
        # print("exp", expense_sheet)
        for line in expense_sheet.expense_line_ids:
            line.petty_id += self.petty_id
        return res


class PettyPayInvoiceWizard(models.TransientModel):
    _inherit = 'petty.pay.invoice.wizard'

     
    def petty_invoice_post_payment(self):
        res = super(PettyPayInvoiceWizard, self).petty_invoice_post_payment()
        for rec in self:
            rec.invoice_id.petty_id += rec.petty_id
            # print(rec.invoice_id.petty_id)
        return res
