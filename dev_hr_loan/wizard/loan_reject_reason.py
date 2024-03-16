# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import api, fields, models, _


class LoanRejectReason(models.TransientModel):
    _name = "loan.reject.reason"

    reason = fields.Text('Reason', required="1")

    def reject_loan(self):
        active_ids = self._context.get('active_ids')
        loan_ids = self.env['employee.loan'].browse(active_ids)
        for loan in loan_ids:
            loan.reject_reason = self.reason
            if loan.state == 'request':
                loan.dep_manager_reject_loan()
            if loan.state == 'dep_approval':
                loan.hr_manager_reject_loan()
        return True


class skip_installment_reject_reason(models.TransientModel):
    _name = "skip.installment.reject.reason"

    reason = fields.Text('Reason', required="1")

    def reject_skip_installment(self):
        active_ids = self._context.get('active_ids')
        installment_ids = self.env['dev.skip.installment'].browse(active_ids)
        for installment in installment_ids:
            installment.reject_reason = self.reason
            if installment.state == 'request':
                installment.dep_reject_skip_installment()
            if installment.state == 'approve':
                installment.hr_reject_skip_installment()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
