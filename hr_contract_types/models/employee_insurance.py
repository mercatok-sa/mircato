# -*- coding: utf-8 -*-

import time
from datetime import datetime,date
from dateutil import relativedelta
from odoo import models, fields, api, _


class EmployeeInsurance(models.Model):
    _name = 'hr.insurance'
    _description = 'HR Insurance'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, help="Employee")
    policy_id = fields.Many2one('insurance.policy', string='Policy', required=True, help="Policy")
    amount = fields.Float(string='Premium', required=True, help="Policy amount")
    sum_insured = fields.Float(string="Sum Insured", required=True, help="Insured sum")
    policy_coverage = fields.Selection([('monthly', 'Monthly'), ('yearly', 'Yearly')],
                                       required=True, default='monthly',
                                       string='Policy Coverage', help="During of the policy")
    date_from = fields.Date(string='Date From',
                            default=time.strftime('%Y-%m-%d'), readonly=True, help="Start date")
    date_to = fields.Date(string='Date To',   readonly=True, help="End date",
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    state = fields.Selection([('active', 'Active'),
                              ('expired', 'Expired'), ],
                             default='active', string="State",compute='get_status')
    company_id = fields.Many2one('res.company', string='Company', required=True, help="Company",
                                 default=lambda self: self.env.user.company_id)

    def get_status(self):
        current_datetime = datetime.now()
        current_date = datetime.strftime(current_datetime, "%Y-%m-%d ")
        for i in self:
            x = str(i.date_from)
            y = str(i.date_to)
            if x <= current_date:
                if y >= current_date:
                    i.state = 'active'
                else:
                    i.state = 'expired'

    @api.constrains('policy_coverage')
    @api.onchange('policy_coverage')
    def get_policy_period(self):
        if self.policy_coverage == 'monthly':
            self.date_to = str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10]
        if self.policy_coverage == 'yearly':
            self.date_to = str(datetime.now() + relativedelta.relativedelta(months=+12))[:10]


class HrInsurance(models.Model):
    _inherit = 'hr.contract'

    insurance_company = fields.Float(string="Company Percentage ", help="Company insurance percentage")
    insurance_employee = fields.Float(string="Employee Percentage ", help="Company insurance percentage")
    deduced_employee_per_month = fields.Float(string="Employee deduced per month", compute="get_deduced_amount", help="Amount that is deduced from employee salary per month")
    deduced_company_per_month = fields.Float(string="Company deduced per month", compute="get_deduced_amount", help="Amount that is paid by the Company per year")
    insurance = fields.One2many('hr.insurance', 'employee_id', string="Insurance", help="Insurance",
                                domain=[('state', '=', 'active')])

    def get_deduced_amount(self):
        current_date = datetime.now()
        current_datetime = datetime.strftime(current_date, "%Y-%m-%d ")
        for cont in self:
            cont.deduced_employee_per_month = ((cont.wage + cont.hra) * cont.insurance_employee)/100
            cont.deduced_company_per_month = ((cont.wage + cont.hra) * cont.insurance_company) / 100




class InsuranceRuleInput(models.Model):
    _inherit = 'hr.payslip'

    deduced_company_per_month = fields.Float(string="Company deduced per year", compute="get_company_insurance_contribution",
                                             help="Amount that is paid by the Company per moth")
    @api.depends('contract_id.deduced_company_per_month')
    def get_company_insurance_contribution(self):
        for rec in self:
           if rec.contract_id:
              print(10* 'm')
              deduced_company = rec.contract_id.deduced_company_per_month
              print(deduced_company)
              rec.deduced_company_per_month = deduced_company
           else:
               rec.deduced_company_per_month = 0.0

#
#     def get_inputs(self, contract_ids, date_from, date_to):
#         res = super(InsuranceRuleInput, self).get_inputs(contract_ids, date_from, date_to)
#         contract_obj = self.env['hr.contract']
#         for i in contract_ids:
#             if contract_ids[0]:
#                 emp_id = contract_obj.browse(i[0].id).employee_id
#                 for result in res:
#                     if emp_id.deduced_amount_per_month != 0:
#                         if result.get('code') == 'INSUR':
#                             result['amount'] = emp_id.deduced_amount_per_month
#         return res
