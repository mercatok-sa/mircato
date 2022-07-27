# -*- coding: utf-8 -*-
from odoo import models


class HrPayslipAcc(models.Model):
    _inherit = 'hr.payslip'

    def _prepare_line_values(self, line, account_id, date, debit, credit):
        value = super(HrPayslipAcc, self)._prepare_line_values(line, account_id, date, debit, credit)
        value['partner_id'] = line.slip_id.employee_id.address_home_id.id
        return value

    # def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
    #     if line.code == 'NET':
    #         return False
    #     else:
    #         return super(HrPayslipAcc, self)._get_existing_lines(line_ids, line, account_id, debit, credit)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    _sql_constraints = [
        ('unique_address_home_id', 'UNIQUE(address_home_id)', 'No duplication of employee address')
    ]
