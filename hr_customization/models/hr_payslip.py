# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = ['hr.payslip', 'mail.thread']
    _name = 'hr.payslip'

    def action_payslip_send(self):
        '''
        This function opens a window to compose an email, with email template
        message loaded by default
        '''

        for rec in self:
            template = self.env.ref('hr_customization.email_template_payslip')
            compose_form = self.env.ref(
                'mail.email_compose_message_wizard_form')
            self = self.with_context(
                default_model='hr.payslip',
                default_res_id=rec.id,
                default_use_template=bool(template),
                default_template_id=template.id,
                default_composition_mode='comment',
                mark_so_as_sent=True
            )
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'target': 'new',
                'context': self.env.context,
            }

    def force_payslip_send(self):
        composer_obj = self.env['mail.compose.message']
        email_act = self.action_payslip_send()
        if email_act and email_act.get('context'):
            composer_values = {}
            email_ctx = email_act['context']
            composer_values.update(composer_obj.onchange_template_id(
                template_id=email_ctx.get('default_template_id'),
                composition_mode=email_ctx.get('default_composition_mode'),
                model=email_ctx.get('default_model'),
                res_id=email_ctx.get('default_res_id')
            ).get('value', {}))
            if not composer_values.get('email_from'):
                composer_values['email_from'] = self.company_id.email

            composer_obj = composer_obj.with_context(
                default_model=email_ctx.get('default_model'),
                default_res_id=email_ctx.get('default_res_id'),
                default_use_template=email_ctx.get('default_use_template'),
                default_template_id=email_ctx.get('default_template_id'),
                default_composition_mode=email_ctx.get(
                    'default_composition_mode'),
                mark_so_as_sent=email_ctx.get('mark_so_as_sent')
            )
            composer = composer_obj.create(composer_values)
            composer.send_mail()
        return True
