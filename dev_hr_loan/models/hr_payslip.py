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


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    installment_ids = fields.Many2many('installment.line', string='Installment Lines')
    installment_amount = fields.Float('Installment Amount', compute='get_installment_amount')
    installment_int = fields.Float('Installment Amount', compute='get_installment_amount')

    def compute_sheet(self):
        for data in self:
            installment_ids = self.env['installment.line'].search(
                [('employee_id', '=', data.employee_id.id), ('loan_id.state', '=', 'done'),
                 ('is_paid', '=', False), ('is_cancelled', '=', False), ('date', '<=', data.date_to),
                 ('loan_id.hold', '=', False)])
            if installment_ids:
                data.installment_ids = [(6, 0, installment_ids.ids)]
        return super(HrPayslip, self).compute_sheet()

    @api.depends('installment_ids')
    def get_installment_amount(self):
        for payslip in self:
            amount = 0
            int_amount = 0
            if payslip.installment_ids:
                for installment in payslip.installment_ids:
                    if not installment.is_skip:
                        amount += installment.installment_amt
                    int_amount += installment.ins_interest

            payslip.installment_amount = amount
            payslip.installment_int = int_amount

    @api.onchange('employee_id')
    def onchange_employee(self):
        if self.employee_id:
            self.installment_ids = False
            installment_ids = self.env['installment.line'].search(
                [('employee_id', '=', self.employee_id.id), ('loan_id.state', '=', 'done'),
                 ('is_paid', '=', False), ('is_cancelled', '=', False), ('date', '<=', self.date_to),
                 ('loan_id.hold', '=', False)])
            if installment_ids:
                self.installment_ids = [(6, 0, installment_ids.ids)]

    @api.onchange('installment_ids')
    def onchange_installment_ids(self):
        if self.employee_id:
            installment_ids = self.env['installment.line'].search(
                [('employee_id', '=', self.employee_id.id), ('loan_id.state', '=', 'done'),
                 ('is_paid', '=', False), ('is_cancelled', '=', False), ('date', '<=', self.date_to),
                 ('loan_id.hold', '=', False)])
            if installment_ids:
                self.installment_ids = [(6, 0, installment_ids.ids)]

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        if self.installment_ids:
            for installment in self.installment_ids:
                installment.send_paid_mail()
                installment.is_paid = True
                installment.payslip_id = self.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
