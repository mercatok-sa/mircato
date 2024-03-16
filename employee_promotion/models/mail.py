# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import date


# from pandas.tseries import offsets


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    promotion_id = fields.Many2one('hr.promotion', string='Promotion')

    def action_send_mail(self):
        for record in self:
            if record.promotion_id:
                record.promotion_id.employee_id.department_id = record.promotion_id.new_department_id
                record.promotion_id.employee_id.job_id = record.promotion_id.new_job_id
                record.promotion_id.promotion_done = True
        return {'type': 'ir.actions.act_window_close', 'infos': 'mail_sent'}
