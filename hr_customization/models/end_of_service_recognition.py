# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class EOSRecongnition(models.Model):
    _name = 'eos.recognition'
    _description = "End Of Service Recognition"
    _rec_name = 'type'

    name = fields.Char(string="Name")
    type = fields.Selection(string="Type", selection=[('department', 'Department'), ('all_employees', 'All Employees')])
    department_id = fields.Many2one('hr.department', string="Department")
    employee_ids = fields.One2many('eos.recognition.indemnity', 'eos_employee_id', string="Employees")
    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('confirmed', 'Confirmed')],
                             default='draft')
    move_id = fields.Many2one('account.move')

    @api.onchange('type', 'department_id')
    def get_employees(self):
        domain = []
        employees = []
        self.employee_ids = False
        if self.department_id and self.type and self.type == 'department':
            domain.append(('department_id', '=', self.department_id.id))
            domain.append(('contract_id', '!=', False))
        elif self.type and self.type == 'all_employees':
            domain.append(('contract_id', '!=', False))
            self.department_id = False
        employee_obj = self.env['hr.employee'].search(domain) if domain else []
        if employee_obj:
            for employee in employee_obj:
                employees.append((0, 0, {
                    'employee_id': employee.id,
                    'indemnity': employee.indemnity_liability
                }))
        self.employee_ids = employees

    def action_compute(self):
        for rec in self:
            if rec.employee_ids:
                rec.employee_ids.mapped('employee_id').get_employee_indemnity_liability()

    def action_confirm(self):
        for rec in self:
            indemnity_liability_account_id = int(
                self.env['ir.config_parameter'].sudo().get_param('indemnity_liability_account_id'))
            indemnity_expense_account_id = int(
                self.env['ir.config_parameter'].sudo().get_param('indemnity_expense_account_id'))
            journal_id = int(self.env['ir.config_parameter'].sudo().get_param('journal_id'))
            if not rec.employee_ids:
                raise ValidationError(_('You can not confirm eos recognition without employees'))
            elif not indemnity_liability_account_id:
                raise ValidationError(_('You should add Indemnity Liability Account in employee configuration'))
            elif not indemnity_expense_account_id:
                raise ValidationError(_('You should add Indemnity Expenses Account in employee configuration'))
            elif not journal_id:
                raise ValidationError(_('You should add Journal in employee configuration'))
            else:
                total_amount = sum(rec.employee_ids.mapped('indemnity'))
                rec.state = 'confirmed'
                vals = {
                    'date': fields.date.today(),
                    'ref': rec.name,
                    'journal_id': journal_id,
                    'company_id': self.env.user.company_id.id
                }
                acc_move_id = self.env['account.move'].create(vals)
                lst = []
                lst.append((0, 0, {
                    'account_id': indemnity_expense_account_id,
                    'name': rec.name,
                    'credit': total_amount,
                }))
                lst.append((0, 0, {
                    'account_id': indemnity_liability_account_id,
                    'name': '/',
                    'debit': total_amount,
                }))
                acc_move_id.line_ids = lst
                if acc_move_id:
                    rec.move_id = acc_move_id.id

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('You cannot delete a confirmed EOS'))
        super(EOSRecongnition, self).unlink()

    def view_journal_entry(self):
        if self.move_id:
            return {
                'view_mode': 'form',
                'res_id': self.move_id.id,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
            }
