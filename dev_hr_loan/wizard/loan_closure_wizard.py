# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class LoanClosureWizard(models.TransientModel):
    _name = "loan.closure.wizard"

    type = fields.Selection(string="Type", selection=[('cash', 'Cash'), ('payslip', 'Payslip'), ])
    date = fields.Date(string="Payslip Date")
    journal_id = fields.Many2one('account.journal', string="Journal")

    def confirm_loan_closure(self):
        active_id = self.env.context.get('active_id', False)
        employee_loan_obj = self.env['employee.loan'].browse(active_id)
        if employee_loan_obj and employee_loan_obj.installment_lines:
            total_loan_value = sum(line.installment_amt for line in
                                   employee_loan_obj.installment_lines.filtered(lambda x: x.is_paid == False))
            if self.type == 'payslip':
                employee_loan_obj.installment_lines.write({
                    'is_cancelled': True
                })
                vals = {
                    'name': 'INS - Loan/Loan Closure',
                    'employee_id': employee_loan_obj.employee_id and employee_loan_obj.employee_id.id or False,
                    'date': self.date,
                    'amount': employee_loan_obj.loan_amount,
                    'installment_amt': total_loan_value,
                    'loan_id': active_id
                }
                self.env['installment.line'].create(vals)
                employee_loan_obj.is_closed = True
            else:
                payment = self.env['account.payment'].create({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': employee_loan_obj.employee_id.address_home_id.id,
                    'amount': total_loan_value,
                    'date': fields.Date.today(),
                    'journal_id': self.journal_id.id,
                    'ref': 'Loan Closure'
                })
                employee_loan_obj.installment_lines.write({
                    'is_cancelled': True
                })
                employee_loan_obj.is_closed = True
                employee_loan_obj.payment_id = payment.id
