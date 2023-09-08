from odoo import models, api, fields
from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools.float_utils import float_compare
from odoo.http import request
from pytz import timezone

import base64

class Provider(models.Model):
    _name = 'provider'

    name = fields.Char('Name',required=True)
    provider = fields.Selection(string='Provider', required=True, selection=[('none', "No Provider Set")], default='none')
    state = fields.Selection(
        string="State",
        selection=[('disabled', "Disabled"), ('enabled', "Enabled")],
        default='enabled', required=True, copy=False)
    company_id = fields.Many2one(  # Indexed to speed-up ORM searches (from ir_rule or others)
        string="Company", comodel_name='res.company', default=lambda self: self.env.company.id,
        required=True)

    # phone change to mobile
    def direct_send_message(self, mobile, message):
        t = type(self)
        fn = getattr(t, f'{self.provider}_direct_send_message', None)
        res = fn(self, mobile, message,)
        return res

    def direct_send_file(self, mobile, attachment_id):
        t = type(self)
        fn = getattr(t, f'{self.provider}_direct_send_file', None)
        res = fn(self, mobile, attachment_id)
        return res

    def send_message(self, recipient, message, quotedMsgId=False):
        t = type(self)
        if self.provider != 'none':
            fn = getattr(t, f'{self.provider}_send_message', None)
            # eval_context = self._get_eval_context(self)
            # active_id = self._context.get('active_id')
            # run_self = self.with_context(active_ids=[active_id], active_id=active_id)
            res = fn(self, recipient, message, quotedMsgId)
            return res
        else:
            raise UserError(_("No Provider Set, Please Enable Provider"))

    def send_file(self, recipient, attachment_id):
        t = type(self)
        fn = getattr(t, f'{self.provider}_send_file', None)
        res = fn(self, recipient, attachment_id)
        return res

    def check_phone(self, mobile):
        t = type(self)
        fn = getattr(t, f'{self.provider}_check_phone', None)
        res = fn(self, mobile)
        return res

    def add_template(self, name, language, category, components):
        t = type(self)
        fn = getattr(t, f'{self.provider}_add_template', None)
        res = fn(self, name, language, category, components)
        return res

    def remove_template(self, name):
        t = type(self)
        fn = getattr(t, f'{self.provider}_remove_template', None)
        res = fn(self, name)
        return res

    def direct_send_template(self, template, language, namespace, mobile, params):
        t = type(self)
        fn = getattr(t, f'{self.provider}_direct_send_template', None)
        res = fn(self, template, language, namespace, mobile, params)
        return res

    def send_template(self, template, language, namespace, partner, params):
        t = type(self)
        fn = getattr(t, f'{self.provider}_send_template', None)
        res = fn(self, template, language, namespace, partner, params)
        return res

    def get_whatsapp_template(self):
        t = type(self)
        fn = getattr(t, f'{self.provider}_get_whatsapp_template', None)
        res = fn(self)
        return res


