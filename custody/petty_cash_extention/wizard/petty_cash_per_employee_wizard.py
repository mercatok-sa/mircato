from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class PettyCashPerEmployeeWizard(models.TransientModel):
    _name = 'petty.cash.per.employee.wizard'

    date_from = fields.Date(string="Start From", required=True)
    date_to = fields.Date(string="End Date", required=True)
    employee_ids = fields.Many2many('hr.employee', string="Employees")

     
    def get_data(self):
        for rec in self:
            data = []

            res = {}
            if rec.date_from and rec.date_to:
                if rec.date_to < rec.date_from:
                    raise ValidationError(_("To date must be greater than from date"))
                date_from = fields.Date.from_string(rec.date_from)
                date_to = fields.Date.from_string(rec.date_to)

                petty_cash_obj = self.env['petty.cash'].search([('employee_id', 'in', rec.employee_ids.ids),
                                                                ('payment_date', '>=', date_from),
                                                                ('payment_date', '<=', date_to)])
            if rec.employee_ids:
                for employee in rec.employee_ids:
                    employee_data = []
                    if petty_cash_obj:
                        for petty in petty_cash_obj:
                            if employee.id == petty.employee_id.id:
                                employee_data.append(
                                    {
                                        'petty_cash_ref': petty.name,
                                        'job_title': petty.employee_id.job_title,
                                        'department': petty.employee_id.department_id.name,
                                        'payment_date': petty.payment_date,
                                        'adjustment_date': petty.adj_date,
                                        'paid_amount': petty.amount,
                                        'balance': petty.balance,
                                        'note': petty.notes,
                                        'status': petty.state
                                    }

                                )

                        data.append({
                            'date_from': rec.date_from,
                            'date_to': rec.date_to,
                            'emp_name': employee.name,
                            'emp_dept': employee.department_id.name,
                            'emp_job': employee.job_id.name,
                            'employee_data': employee_data

                        })


            else:
                raise ValidationError(_('No Data!'))

            res['data'] = data
            return self.env.ref('petty_cash_extention.petty_cash_per_employee_report_id').report_action(self, data=res)
