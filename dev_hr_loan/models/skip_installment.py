# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class DevSkipInstallment(models.Model):
    _name = 'dev.skip.installment'
    _inherit = 'mail.thread'
    _order = 'name desc'

    @api.model
    def _get_employee(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee_id

    @api.model
    def _get_default_user(self):
        return self.env.user

    name = fields.Char('Name', default='/')
    employee_id = fields.Many2one('hr.employee', string='Employee', required="1", default=_get_employee)
    loan_id = fields.Many2one('employee.loan', string='Loan', required="1")
    installment_id = fields.Many2one('installment.line', string='Installment', required="1")
    date = fields.Date('Date', default=fields.Date.today())
    user_id = fields.Many2one('res.users', string='User', default=_get_default_user)
    notes = fields.Text('Reason', required="1")
    manager_id = fields.Many2one('hr.employee', string='Department Manager', required="1")
    skip_installment_url = fields.Char('URL', compute='get_url')
    hr_manager_id = fields.Many2one('hr.employee', string='HR Manager')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    is_dm = fields.Boolean('Department Manager', compute='is_department_manager')
    move_id = fields.Many2one('account.move', string='Journal Entry', copy=False)
    reject_reason = fields.Text('Reject Reason', copy=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('request', 'Submit Request'),
                              ('approve', 'Approve'),
                              ('hr_manager_approve', 'Hr Manger Approve'),
                              ('confirm', 'Confirm'),
                              ('done', 'Done'),
                              ('reject', 'Reject'),
                              ('cancel', 'Cancel'), ], string='State', default='draft', track_visibility='onchange')
    method = fields.Selection(string="Method", selection=[('pay_next_month', 'Pay Next Month'),
                                                          ('postpone', 'Postpone')],
                              default='pay_next_month')

    @api.depends('employee_id', 'manager_id', 'state')
    def is_department_manager(self):
        for loan in self:
            if loan.manager_id:
                if loan.manager_id.user_id.id == self.env.user.id:
                    loan.is_dm = True
                else:
                    loan.is_dm = False
            else:
                loan.is_dm = False

    @api.depends('installment_id')
    def get_url(self):
        for installment in self:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url', default='http://localhost:8069')
            if base_url:
                base_url += '/web/login?db=%s&login=%s&key=%s#id=%s&model=%s' % (
                    self._cr.dbname, '', '', installment.id, 'dev.skip.installment')
                installment.skip_installment_url = base_url

    @api.constrains('installment_id')
    def _Check_skip_installment(self):
        request_ids = False
        if self.employee_id and self.installment_id:
            request_id = self.search([('employee_id', '=', self.employee_id.id),
                                      ('installment_id', '=', self.installment_id.id),
                                      ('state', 'in', ['draft', 'approve', 'confirm', 'done']), ('id', '!=', self.id)])
        request = len(request_id)
        if request > 0:
            raise ValidationError("This %s  installement of skip request has been %s state" % (
                self.installment_id.name, request_id.state))

    @api.onchange('loan_id')
    def onchange_loan_id(self):
        if self.loan_id:
            self.manager_id = self.loan_id.manager_id

    def action_send_request(self):
        if not self.manager_id:
            raise ValidationError(_('Please Select Department manager'))
        if self.manager_id and self.manager_id.id != self.loan_id.manager_id.id:
            raise ValidationError(_('Loan Manager and selected department manager not same'))
        if self.manager_id and self.manager_id.work_email:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('dev_hr_loan',
                                                             'dev_skip_dep_manager_approval')
            mtp = self.env['mail.template']
            template_id = mtp.browse(template_id[1])
            template_id.write({'email_to': self.manager_id.work_email})
            s = template_id.send_mail(self.ids[0], True)
        self.state = 'request'

    def get_hr_manager_email(self):
        group_id = self.env['ir.model.data'].get_object_reference('hr', 'group_hr_manager')[1]
        group_ids = self.env['res.groups'].browse(group_id)
        email = ''
        if group_ids:
            employee_ids = self.env['hr.employee'].search([('user_id', 'in', group_ids.users.ids)])
            for emp in employee_ids:
                if email:
                    email = email + ',' + emp.work_email
                else:
                    email = emp.work_email
        return email

    def approve_skip_installment(self):
        email = self.get_hr_manager_email()
        if email:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('dev_hr_loan',
                                                             'dev_skip_ins_hr_manager_request')
            mtp = self.env['mail.template']
            template_id = mtp.browse(template_id[1])
            template_id.write({'email_to': email})
            template_id.send_mail(self.ids[0], True)
        self.state = 'approve'

    def dep_reject_skip_installment(self):
        if self.employee_id.work_email:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('dev_hr_loan',
                                                             'dep_manager_reject_skip_installment')

            mtp = self.env['mail.template']
            template_id = mtp.browse(template_id[1])
            template_id.write({'email_to': self.employee_id.work_email})
            template_id.send_mail(self.ids[0], True)

        self.state = 'reject'

    def hr_reject_skip_installment(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        self.hr_manager_id = employee_id and employee_id.id or False
        if self.employee_id.work_email and self.hr_manager_id:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('dev_hr_loan',
                                                             'hr_manager_reject_skip_installment')

            mtp = self.env['mail.template']
            template_id = mtp.browse(template_id[1])
            template_id.write({'email_to': self.employee_id.work_email})
            template_id.send_mail(self.ids[0], True)

        self.state = 'reject'

    def confirm_skip_installment(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        self.hr_manager_id = employee_id and employee_id.id or False
        if self.employee_id.work_email and self.hr_manager_id:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('dev_hr_loan',
                                                             'hr_manager_confirm_skip_installment')

            mtp = self.env['mail.template']
            template_id = mtp.browse(template_id[1])
            template_id.write({'email_to': self.employee_id.work_email})
            template_id.send_mail(self.ids[0], True)

        self.state = 'confirm'

    def view_journal_entry(self):
        if self.move_id:
            return {
                'view_mode': 'form',
                'res_id': self.move_id.id,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
            }

    def create_skip_account_journal_entry(self):
        if not self.employee_id.address_home_id:
            raise ValidationError(_('Employee Private Address is not selected in Employee Form !!!'))

        vals = {
            'date': self.date,
            'ref': self.name,
            'journal_id': self.loan_id.loan_type_id.journal_id and self.loan_id.loan_type_id.journal_id.id,
            'company_id': self.company_id.id
        }
        acc_move_id = self.env['account.move'].create(vals)
        lst = []
        lst.append((0, 0, {
            'account_id': self.loan_id.loan_type_id and self.loan_id.loan_type_id.loan_account.id,
            'partner_id': self.employee_id.address_home_id and self.employee_id.address_home_id.id or False,
            'name': self.name,
            'credit': self.installment_id.ins_interest or 0.0,
        }))
        credit_account = False
        if self.employee_id.address_home_id and self.employee_id.address_home_id.property_account_receivable_id:
            credit_account = self.employee_id.address_home_id.property_account_receivable_id.id or False

        lst.append((0, 0, {
            'account_id': credit_account or False,
            'partner_id': self.employee_id.address_home_id and self.employee_id.address_home_id.id or False,
            'name': '/',
            'debit': self.installment_id.ins_interest or 0.0,
        }))
        acc_move_id.line_ids = lst
        if acc_move_id:
            self.move_id = acc_move_id.id
        return True

    def done_skip_installment(self):
        date = self.installment_id.date
        if self.method == 'pay_next_month':
            date = date + relativedelta(months=1)
        else:
            date = self.loan_id.installment_lines[-1].date + relativedelta(months=1)
        vals = {
            'name': str(self.installment_id.name) + ' - COPY',
            'employee_id': self.employee_id and self.employee_id.id or False,
            'date': date,
            'amount': self.installment_id.amount,
            'interest': self.installment_id.interest,
            'installment_amt': self.installment_id.installment_amt,
            'ins_interest': self.installment_id.ins_interest,
            'loan_id': self.installment_id.loan_id.id,
        }
        new_inst = self.env['installment.line'].create(vals)
        if new_inst:
            self.installment_id.is_skip = True
            self.installment_id.installment_amt = 0.0
        self.create_skip_account_journal_entry()
        self.state = 'done'

    def cancel_skip_installment(self):
        self.state = 'cancel'

    def set_to_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'dev.skip.installment') or '/'
        return super(DevSkipInstallment, self).create(vals)

    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = '/'
        return super(DevSkipInstallment, self).copy(default=default)

    def unlink(self):
        for skp_installment in self:
            if skp_installment.state != 'draft':
                raise ValidationError(_('Skip Installment delete in draft state only !!!'))
        return super(DevSkipInstallment, self).unlink()

    def hr_manger_approve(self):
        self.ensure_one()
        self.state = 'hr_manager_approve'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
