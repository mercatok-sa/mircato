# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'HR Employee Documents'

    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            exp_date = each.expiry_date
            if exp_date < date.today():
                raise ValidationError('Your Document Is Already Expired.')

    name = fields.Char(string='Document Number', required=True, copy=False)
    document_name = fields.Many2one('employee.checklist', string='Document', required=False)
    description = fields.Text(string='Description', copy=False)
    expiry_date = fields.Date(string='Expiry Date', copy=False)
    employee_ref = fields.Many2one('hr.employee', copy=False, string='Employee')
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    issue_date = fields.Date(string='Issue Date', default=fields.Date.context_today, copy=False)

    @api.model
    def mail_reminder(self):
        users = []
        date_now = fields.Date().today()
        match = self.search([])
        for user in self.env['res.users'].search([]):
            if user.has_group('hr.group_hr_manager'):
                users.append(user.partner_id.id)
        for i in match:
            if i.expiry_date:
                exp_date = i.expiry_date
                if date_now == exp_date:
                    mail_content = "  Hello  " + i.employee_ref.name + ",<br>Your Document " + i.name + "is going to expire on " + \
                                   str(i.expiry_date) + ". Please renew it before expiry date"
                    if len(users) > 0:
                        users = set(users)
                    post_vars = {'subject': _('Document-%s Expired On %s') % (i.name, i.expiry_date),
                                 'title': 'Document Expiration',
                                 'body': mail_content,
                                 'partner_ids': [(6, 0, users)]
                                 }

                    self.env['mail.thread'].message_post(type="notification", subtype="mt_comment", **post_vars)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_count = fields.Integer(compute="document_count_s", string='# Documents')

    def document_count_s(self):
        self.document_count = len(self.env['hr.employee.document'].search([('employee_ref', '=', self.id)]))

    def document_view(self):
        self.ensure_one()
        domain = [
            ('employee_ref', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'hr.employee.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': {'default_employee_ref': self.id}
        }


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('hr.employee.document', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Attachment", invisible=1)
