# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime



#ayman

# class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
#
#     _inherit = "hr.expense.sheet.register.payment.wizard"
#
#     def _get_payment_vals(self):
#        # print(self.env.context)
#
#        res =  super(HrExpenseSheetRegisterPaymentWizard, self)._get_payment_vals()
#        expense_sheet = self.env['hr.expense.sheet'].browse(self.env.context.get('active_id'))
#
#        res.update({'expens_id':expense_sheet.id})
#        return res