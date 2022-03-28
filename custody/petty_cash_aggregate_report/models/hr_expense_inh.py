# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrExpenseSheet(models.Model):

    _inherit= "hr.expense"

    petty_id = fields.Many2many('petty.cash',string='Petty Cash')

    # branch_id = fields.Many2one(comodel_name="res.branch", string="Branch", )

     
    def action_submit_expenses(self):
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))

        todo = self.filtered(lambda x: x.payment_mode == 'own_account') or self.filtered(
            lambda x: x.payment_mode == 'company_account')
        return {
            'name': _('New Expense Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense.sheet',
            'target': 'current',
            'context': {
                'default_expense_line_ids': todo.ids,
                'default_employee_id': self[0].employee_id.id,
                # 'default_branch_id': self[0].branch_id.id,
                'default_name': todo[0].name if len(todo) == 1 else ''
            }
        }

