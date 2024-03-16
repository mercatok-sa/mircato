from odoo import fields, models, api, _
from datetime import date


class PenaltyRequest(models.Model):
    _inherit = 'penalty.request'

    penalty_rule_id = fields.Many2one(comodel_name='penalty.rule')
    contract_id = fields.Many2one(required=False, related="employee_id.contract_id")
    month = fields.Char(compute='get_month')
    state = fields.Selection(selection_add=[('employee_submit', 'Employee Submit'),
                                            ('emp_mang_submit', 'Manager Submit'),
                                            ('hr_mang_submit', 'Hr Manager Submit'),
                                            ('approved', 'Approved'), ('rejected',)])

    @api.depends('request_date')
    def get_month(self):
        for item in self:
            item.month = ''
            if item.request_date:
                item.month = item.request_date.month

    employee_cause_of_penalty = fields.Text()
    employee_approve_of_cause = fields.Text()
    employee_other_approve = fields.Text()
    emp_manager_feedback = fields.Text()
    emp_manager_opinion = fields.Selection(selection=[('approved', 'غير مخالف'), ('not_approved', 'مخالف')])
    hr_manager_feedback = fields.Text()
    no_of_repetition = fields.Integer()
    last_penalty_date = fields.Date(compute='get_last_penalty_date')

    @api.depends('employee_id')
    def get_last_penalty_date(self):
        for rec in self:
            rec.last_penalty_date = False
            if rec.employee_id:
                rec.last_penalty_date = self.env['penalty.request'].search(
                    [('employee_id', '=', rec.employee_id.id),
                     ('state', '=', 'approved')], order='id desc', limit=1).request_date

    @api.onchange('penalty_rule_id')
    def onchange_penalty_rule_id(self):
        for rec in self:
            if rec.penalty_rule_id:
                rec.penalty_type = rec.penalty_rule_id.penalty_type
                previous_same_penalty = self.env['penalty.request'].search_count(
                    [('employee_id', '=', rec.employee_id.id),
                     ('penalty_rule_id', '=', rec.penalty_rule_id.id), ('month', '=', date.today().month),
                     ('state', 'not in', ('draft', 'rejected'))])

                lines = [line.rate for line in rec.penalty_rule_id.line_ids]
                print(len(lines))
                if len(lines) > 0:
                    if previous_same_penalty == 0:
                        rec.penalty_amount_amount = lines[0]
                        rec.penalty_amount_days = lines[0]
                    elif previous_same_penalty == 1:
                        rec.penalty_amount_amount = lines[1]
                        rec.penalty_amount_days = lines[1]
                        rec.no_of_repetition = 1
                    elif previous_same_penalty == 2:
                        rec.penalty_amount_amount = lines[2]
                        rec.penalty_amount_days = lines[2]
                        rec.no_of_repetition = 2
                    elif previous_same_penalty == 3:
                        rec.penalty_amount_amount = lines[3]
                        rec.penalty_amount_days = lines[3]
                        rec.no_of_repetition = 3
                    elif previous_same_penalty == 4:
                        rec.penalty_amount_amount = lines[4]
                        rec.penalty_amount_days = lines[4]
                        rec.no_of_repetition = 4
                    elif previous_same_penalty >= 5:
                        rec.penalty_amount_amount = lines[5]
                        rec.penalty_amount_days = lines[5]
                        rec.no_of_repetition += 1

    @api.model
    def create(self, vals):
        res = super(PenaltyRequest, self).create(vals)
        users, users_manager = [], []
        users.append(res.employee_id.user_id.id)
        if res.employee_id.parent_id:
            users_manager.append(res.employee_id.parent_id.user_id.id)
        if users:
            template = self.env.ref('penalty_enhancement.mail_penalty_request_template')
            email_users = self.env['res.users'].sudo().search([('id', 'in', users)]).mapped('email')
            if email_users:
                if False in email_users:
                    email_users.remove(False)
            template.write({'email_to': ', '.join(email_users)})
            template.send_mail(res.id, force_send=True, raise_exception=False)
        if users_manager:
            m_template = self.env.ref('penalty_enhancement.mail_penalty_request_manager_template')
            m_email_users = self.env['res.users'].sudo().search([('id', 'in', users_manager)]).mapped('email')
            if m_email_users:
                if False in m_email_users:
                    m_email_users.remove(False)
            m_template.write({'email_to': ', '.join(m_email_users)})
            m_template.send_mail(res.id, force_send=True, raise_exception=False)
        return res

    def confirm_button(self):
        res = super(PenaltyRequest, self).confirm_button()
        users, users_manager = [], []
        users.append(self.employee_id.user_id.id)
        if self.employee_id.parent_id:
            users_manager.append(self.employee_id.parent_id.user_id.id)
        if users:
            template = self.env.ref('penalty_enhancement.mail_penalty_request_template')
            email_users = self.env['res.users'].sudo().search([('id', 'in', users)]).mapped('email')
            if email_users:
                if False in email_users:
                    email_users.remove(False)
            template.write({'email_to': ', '.join(email_users)})
            template.send_mail(self.id, force_send=True, raise_exception=False)
        if users_manager:
            m_template = self.env.ref('penalty_enhancement.mail_penalty_request_manager_template')
            m_email_users = self.env['res.users'].sudo().search([('id', 'in', users_manager)]).mapped('email')
            if m_email_users:
                if False in m_email_users:
                    m_email_users.remove(False)
            m_template.write({'email_to': ', '.join(m_email_users)})
            m_template.send_mail(self.id, force_send=True, raise_exception=False)
        return res

    def action_approve(self):
        self.write({'state': 'approved'})
