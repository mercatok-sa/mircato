# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string="Loan Installment", help="Loan installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_contract(self, employee, date_from, date_to):

        """
        @param employee: recordset of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open'), '|',
                        '|'] + clause_1 + clause_2 + clause_3
        return self.env['hr.contract'].search(clause_final).ids

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []

        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(str(date_from), "%Y-%m-%d")))
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (
            employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        # if not self.contract_id.struct_id:
        #     return
        # self.struct_id = self.contract_id.struct_id

        # computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        print(19*"ali", contracts, date_from, date_to)
        # worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        # worked_days_lines = self.worked_days_line_ids.browse([])
        # for r in worked_days_line_ids:
        #     worked_days_lines += worked_days_lines.new(r)
        # self.worked_days_line_ids = worked_days_lines
        if contracts:
            input_line_ids = self.get_inputs(contracts, date_from, date_to)
            print(input_line_ids,"uuuuuuuuuu")
            input_lines = self.input_line_ids.browse([])
            print(input_lines,"assssssss")


        if input_line_ids:
            for r in input_line_ids:
                input_lines += input_lines.new(r)
                print(input_lines)
            self.input_line_ids = input_lines
        return



    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        # res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        res = []
        # inputs = self.env.ref("hr_rule_loan").id
        inputs = self.env['hr.salary.rule'].search([])
        for contract in contract_ids:
            for input in inputs:
                if input.code == 'LO':
                   input_data = {
                    'name': input.name,
                    'code': input.code,
                    'contract_id': self.contract_id,
                    'payslip_id':self.id,
                    'input_type_id': self.env.ref("hr_loan.hr_rule_input_type_loan").id,
                    'code'  : input.code,
                    'sequence': 16
                   }
                   res += [input_data]
                   print(res)
        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0].id).employee_id
        lon_obj = self.env['hr.loan'].search([('employee_id', '=', emp_id.id), ('state', '=', 'approve')])
        for loan in lon_obj:
            print("The loan is goted"*10)
            for loan_line in loan.loan_lines:
                if date_from <= loan_line.date <= date_to and not loan_line.paid:
                    print("osman"*10)
                    for result in res:
                        if result.get("code") == 'LO':
                            print("The loan line is goted" * 10)
                            result['amount'] = loan_line.amount
                            result['loan_line_id'] = loan_line.id
                            # print(res['loan_line_id'])

                            return res

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.paid = True
                line.loan_line_id.loan_id._compute_loan_amount()
        return super(HrPayslip, self).action_payslip_done()
