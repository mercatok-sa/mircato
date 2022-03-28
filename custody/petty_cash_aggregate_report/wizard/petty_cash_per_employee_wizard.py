# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
import itertools


class PettyCashPerEmployeeWizard(models.TransientModel):
    _name = 'petty.cash.aggregate.employee.wizard'

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    employee_ids = fields.Many2many('hr.employee', string="Employees")
    product_ids = fields.Many2many('product.product', string="Product", domain=[('type', '=', 'service')])
    print_petty_cash = fields.Boolean(string="Petty Cash", default=True)
    print_expenses = fields.Boolean(string="Expenses", default=True)
    print_bills = fields.Boolean(string="Vendor Bills", default=True)
    print_invoices = fields.Boolean(string="Customer Invoices", default=True)
    petty_cash_ids = fields.Many2many('petty.cash')

    @api.onchange('petty_cash_ids')
    def onchange_petty_set_petty_employees(self):
        for rec in self:
            rec.employee_ids = False
            emps = []
            for petty in rec.petty_cash_ids:
                emps.append(petty.employee_id.id)
            rec.employee_ids = emps
            return

     
    def get_data(self):
        for rec in self:
            data = []
            net_balance = 0
            res = {}
            if rec.date_from and rec.date_to:
                if rec.date_to < rec.date_from:
                    raise ValidationError(_("To date must be greater than from date"))
                date_from = fields.Date.from_string(rec.date_from)
                date_to = fields.Date.from_string(rec.date_to)

                petty_domain =  [('employee_id', 'in', rec.employee_ids.ids),
                                                                ('payment_date', '>=', date_from),
                                                                ('payment_date', '<=', date_to),
                                                                ('inv_ref', '=', False),
                                                                ]
                if rec.petty_cash_ids:
                    petty_domain.append(
                        ('id','in',rec.petty_cash_ids.ids)
                    )
                petty_cash_obj = self.env['petty.cash'].search(petty_domain)
                bill_domain = [('employee_id', 'in', rec.employee_ids.ids),
                                                                ('invoice_date', '>=', date_from),
                                                                ('move_type', '=', 'in_invoice'),
                                                                ('petty_id', '!=', False),
                                                                ('invoice_date', '<=', date_to)]
                if rec.petty_cash_ids:
                    bill_domain.append(
                        ('petty_id','in',rec.petty_cash_ids.ids)
                    )                                                
                bill_objs = self.env['account.move'].search(bill_domain)
                group_bills_dict = {}
                for record in bill_objs:
                    group_bills_dict.setdefault(record.employee_id, []).append(record)
                # print(bill_objs, "////", group_bills_dict)
                inv_petty_cash_obj = self.env['petty.cash'].search([('employee_id', 'in', rec.employee_ids.ids),
                                                                    ('payment_date', '>=', date_from),
                                                                    ('payment_date', '<=', date_to),
                                                                    ('inv_ref', '!=', False),
                                                                                     ])
                group_petty_dict = {}
                for record in inv_petty_cash_obj:
                    group_petty_dict.setdefault(record.employee_id, []).append(record)
                # print(inv_petty_cash_obj, "////", group_petty_dict)
                domain = [('employee_id', 'in', rec.employee_ids.ids),
                          ('date', '>=', date_from),
                          # ('petty_id', '!=', False),
                          ('date', '<=', date_to)]

                if rec.petty_cash_ids:
                    domain.append(
                        ('petty_id','in',rec.petty_cash_ids.ids)
                    ) 
                if rec.product_ids:
                    domain.append(
                        ('product_id', 'in', rec.product_ids.ids)
                    )

                expense_objs = self.env['hr.expense'].search(domain)
                group_exp_dict = {}
                for record in expense_objs:
                    group_exp_dict.setdefault(record.employee_id, []).append(record)
                # print(expense_objs, "////", group_exp_dict)
            ff = False
            if rec.employee_ids:
                for employee in rec.employee_ids:
                    tbalance1 = 0
                    tamt1 = 0
                    tbalance2 = 0
                    tamt2 = 0
                    employee_data = []
                    employee_data_petty = []
                    employee_data_bill = []
                    employee_data_exp = []
                    if petty_cash_obj:
                        for petty in petty_cash_obj:
                            if employee.id == petty.employee_id.id:
                                employee_data.append({
                                        'petty_cash_ref': petty.name,
                                        'note': petty.notes,
                                        'job_title': petty.employee_id.job_title,
                                        'department': petty.employee_id.department_id.name,
                                        'payment_date': petty.payment_date,
                                        'adjustment_date': petty.adj_date,
                                        'paid_amount': petty.amount,
                                        'balance': petty.balance,
                                        'status': petty.state
                                    })

                                net_balance += petty.amount
                                if self.print_petty_cash:
                                    tbalance1 += petty.balance
                                    tamt1 += petty.amount
                    # print(employee_data)

                    for r in group_petty_dict:
                        if employee == r:
                            for petty_record in group_petty_dict.get(r):
                                employee_data_petty.append(
                                    {
                                        'inv_ref': petty_record.inv_ref,
                                        'emp_name': petty_record.employee_id.name,
                                        'job_title': petty_record.employee_id.job_title,
                                        'department': petty_record.employee_id.department_id.name,
                                        'payment_date': petty_record.payment_date,
                                        'adjustment_date': petty_record.adj_date,
                                        'paid_amount': petty_record.amount,
                                        'balance': petty_record.balance,
                                        'status': petty_record.state
                                    }

                                )
                                net_balance += petty_record.amount
                                if self.print_invoices:
                                    tbalance1 += petty_record.balance
                                    tamt1 += petty_record.amount
                    ff=False
                    for r in group_exp_dict:
                        if employee == r:
                            for exp_record in group_exp_dict.get(r):
                                line = ''
                                i=0
                                # for x in exp_record.petty_id:
                                #     i+=1
                                #     if i%2==0:
                                #         line += x.name + ',\n'
                                #     else:
                                #         line += x.name + ','

                                for x in exp_record.petty_id:
                                    if not rec.petty_cash_ids.ids:
                                        i+=1
                                        if i%2==0:
                                            line += x.name + ',\n'
                                        else:
                                            line += x.name + ','
                                    else:
                                        if x.id in rec.petty_cash_ids.ids:
                                            i+=1
                                            if i%2==0:
                                                line += x.name + ',\n'
                                            else:
                                                line += x.name + ','


                                if exp_record.reference:
                                    ff=True
                                employee_data_exp.append(
                                    {'date': exp_record.date,
                                     'product': exp_record.product_id.name,
                                     'name': exp_record.name,
                                     'petty_ref': line,
                                     'price': exp_record.unit_amount,
                                     'quantity': exp_record.quantity,
                                     'unit': exp_record.product_uom_id.name,
                                     'total': exp_record.total_amount,
                                     'ref': exp_record.reference,
                                     'status': 'Paid' if exp_record.state=='done' else exp_record.state
                                     }

                                )
                                net_balance -= exp_record.total_amount
                                # tbalance2 += petty.balance
                                if self.print_expenses:
                                    tamt2 += exp_record.total_amount
                    for r in group_bills_dict:
                        if employee == r:
                            for bill_record in group_bills_dict.get(r):
                                line=''
                                balance=0
                                for x in bill_record.petty_id:
                                    if not rec.petty_cash_ids.ids:
                                        line+=x.name+','
                                        balance+=x.balance
                                    else:
                                        if x.id in rec.petty_cash_ids.ids:
                                            line+=x.name+','
                                            balance+=x.balance
                                employee_data_bill.append(
                                    {'bill_ref': bill_record.name,
                                     'emp_name': bill_record.employee_id.name,
                                     'petty_ref':line ,
                                     'job_title': bill_record.employee_id.job_title,
                                     'department': bill_record.employee_id.department_id.name,
                                     'paid_amount': bill_record.amount_total- bill_record.amount_residual,
                                    #  'paid_amount': bill_record.amount_total- bill_record.amount_total,
                                     'balance': balance,
                                     'status': bill_record.state
                                     }

                                )
                                # net_balance -= (bill_record.amount_total- bill_record.residual)
                                net_balance -= (bill_record.amount_total- bill_record.amount_total)
                                if self.print_bills:
                                    # tamt2 += bill_record.amount_total- bill_record.residual
                                    tamt2 += bill_record.amount_total- bill_record.amount_total
                    data.append({
                        'date_from': rec.date_from,
                        'date_to': rec.date_to,
                        'emp_name': employee.name,
                        'emp_dept': employee.department_id.name,
                        'emp_job': employee.job_id.name,
                        'employee_data': employee_data,
                        'employee_data_petty': employee_data_petty,
                        'employee_data_bill': employee_data_bill,
                        'employee_data_exp': employee_data_exp,
                        'net_balance': net_balance,
                        'tbalance1': tbalance1,
                        'tamt1': tamt1,
                        'tamt2': tamt2,
                        'print_petty_cash': rec.print_petty_cash,
                        'print_expenses': rec.print_expenses,
                        'print_bills': rec.print_bills,
                        'print_invoices': rec.print_invoices,
                        'ff':ff

                    })








            else:
                raise ValidationError(_('No Data!'))

            res['data'] = data
            return self.env.ref('petty_cash_aggregate_report.petty_cash_aggregate_employee_report_id').report_action(
                self, data=res)
