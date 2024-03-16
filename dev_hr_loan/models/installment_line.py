# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class installment_line(models.Model):
    _name = 'installment.line'
    _order = 'date,name'

    name = fields.Char('Name')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    loan_id = fields.Many2one('employee.loan', string='Loan', required="1", ondelete='cascade')
    date = fields.Date('Date')
    is_paid = fields.Boolean('Paid')
    is_cancelled = fields.Boolean('Cancelled')
    amount = fields.Float('Loan Amount')
    interest = fields.Float('Total Interest')
    ins_interest = fields.Float('Interest')
    installment_amt = fields.Float('Installment Amt')
    total_installment = fields.Float('Total', compute='get_total_installment')
    payslip_id = fields.Many2one('hr.payslip', string='Payslip')
    is_skip = fields.Boolean('Skip Installment')

    @api.depends('installment_amt', 'ins_interest')
    def get_total_installment(self):
        for line in self:
            line.total_installment = line.ins_interest + line.installment_amt

    def send_paid_mail(self):
        if self.employee_id and self.employee_id.work_email:
            template_id = self.env['ir.model.data'].get_object_reference('dev_hr_loan',
                                                                         'dev_employee_installment_paid_send_mail')

            template_id = self.env['mail.template'].browse(template_id[1])
            template_id.send_mail(self.ids[0], True)
        return True

    def action_view_payslip(self):
        if self.payslip_id:
            return {
                'view_mode': 'form',
                'res_id': self.payslip_id.id,
                'res_model': 'hr.payslip',
                'type': 'ir.actions.act_window',

            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
