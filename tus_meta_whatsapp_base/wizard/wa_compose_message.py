import ast
import base64
import re

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

class WAComposer(models.TransientModel):

    _name = 'wa.compose.message'
    _description = 'Whatsapp composition wizard'

    @api.model
    def default_get(self, fields):
        result = super(WAComposer, self).default_get(fields)
        active_model = False
        active_id = False

        # Multi Companies and Multi Providers Code Here
        if self.env.user:
            provider_id = self.env.user.provider_ids.filtered(lambda x: x.company_id == self.env.company)
            if provider_id:
                result['provider_id'] = provider_id[0].id

        if 'model' in result:
            active_model = result.get('model')
            active_id = result.get('res_id')
        else:
            active_model = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')
        if active_model:
            record = self.env[active_model].browse(active_id)
            if 'template_id' in result:
                template = self.env['wa.template'].browse(result.get('template_id'))
                result['body'] = template._render_field('body_html', [record.id], compute_lang=True)[
                    record.id]
            if active_model == 'res.partner':
                result['partner_id'] = record.id
            else:
                if record.partner_id:
                    result['partner_id'] = record.partner_id.id
                else:
                    result['partner_id'] = False
            if 'report' in self.env.context:
                report = str(self.env.context.get('report'))
                report_id = self.env.ref(report).sudo()
                pdf = report_id._render_qweb_pdf(record.id)
                Attachment = self.env['ir.attachment'].sudo()
                b64_pdf = base64.b64encode(pdf[0])
                name=''
                if active_model == 'res.partner':
                    if report == 'account_followup.action_report_followup':
                        name = 'Followups-%s' % record.id
                elif active_model == 'stock.picking':
                    name = ((record.state in ('done') and _('Delivery slip - %s') % record.name) or
                            _('Picking Operations - %s') % record.name)
                elif active_model == 'account.move':
                    name = ((record.state in ('posted') and  record.name)  or
                            _('Draft - %s') % record.name)
                else:
                    name = ((record.state in ('draft', 'sent') and _('Quotation - %s') % record.name) or
                            _('Order - %s') % record.name)

                name = '%s.pdf' % name
                attac_id = Attachment.search([('name', '=', name)], limit=1)
                if report == 'account_followup.action_report_followup':
                    attac_id = Attachment
                if len(attac_id) == 0:
                    attac_id = Attachment.create({'name': name,
                                                  'type': 'binary',
                                                  'datas': b64_pdf,
                                                  'res_model': 'whatsapp.history',
                                                  })
                if active_model == 'res.partner':
                    result['partner_id'] = record.id
                else:
                    if record.partner_id:
                        result['partner_id'] = record.partner_id.id
                    else:
                        result['partner_id'] = False
                result['attachment_ids'] = [(4, attac_id.id)]
        return result

    def _get_current_model_template(self):
        domain=[]
        active_model = False
        if self.env.context.get('active_model'):
            active_model = str(self.env.context.get('active_model'))
        elif self.env.context.get('default_model'):
            active_model = str(self.env.context.get('default_model'))
        else:
            active_model = self.model
        domain = [('model', '=', active_model),('state','=','added')]

        # Multi Companies and Multi Providers Code Here
        #provider_id = self.env.user.provider_ids.filtered(lambda x: x.company_id == self.env.company)
        # if self.env.user.provider_id:
        if self.env.user:
            provider_id = self.env.user.provider_ids.filtered(lambda x: x.company_id == self.env.company)
            if provider_id:
                provider_id = provider_id[0]

        if provider_id:
            domain.append(('provider_id', '=', provider_id.id))
        else:
            domain.append(('create_uid', '=', self.env.user.id))
        return domain


    body = fields.Html('Contents', default='', sanitize_style=True)
    partner_id = fields.Many2one(
        'res.partner')
    template_id = fields.Many2one(
        'wa.template', 'Use template', index=True, domain=_get_current_model_template
       )
    attachment_ids = fields.Many2many(
        'ir.attachment', 'wa_compose_message_ir_attachments_rel',
        'wa_wizard_id', 'attachment_id', 'Attachments')
    model = fields.Char('Related Document Model', index=True)
    res_id = fields.Integer('Related Document ID', index=True)
    provider_id = fields.Many2one('provider', 'Provider')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    allowed_provider_ids = fields.Many2many('provider', 'Provider', compute='update_allowed_providers')

    @api.depends('company_id')
    def update_allowed_providers(self):
        self.allowed_provider_ids = self.env.user.provider_ids

    @api.onchange('company_id', 'provider_id')
    def onchange_company_provider(self):
        self.template_id = False
        return {'domain': {'template_id': [('model_id.model', '=', self._context.get('active_model') or self._context.get('default_model')), ('provider_id', '=', self.provider_id.id)]}}
    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        if 'active_model' in self.env.context:
            active_model = str(self.env.context.get('active_model'))
            active_record = self.env[active_model].browse(self.env.context.get('active_id'))
            for record in self:
                if record.template_id:
                    record.body = record.template_id._render_field('body_html', [active_record.id], compute_lang=True)[active_record.id]
                else:
                    record.body = ''
        else:
            active_record = self.env[self.model].browse(self.res_id)
            for record in self:
                if record.template_id:
                    record.body = record.template_id._render_field('body_html', [active_record.id], compute_lang=True)[
                        active_record.id]
                else:
                    record.body = ''

    def send_whatsapp_message(self):
        if self.env.context.get('active_model'):
            active_model = str(self.env.context.get('active_model'))
            active_id = self.env.context.get('active_id')
        else:
            active_model = self.model
            active_id = self.res_id
        record = self.env[active_model].browse(active_id)
        if active_model in ['sale.order','purchase.order']:
            record.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        user_partner = self.env.user.partner_id
        # users = self.env['res.users'].sudo().search([])
        part_lst = []
        part_lst.append(self.partner_id.id)
        part_lst.append(user_partner.id)

        # Multi Companies and Multi Providers Code Here
        provider_id = self.provider_id
        # provider_id = self.env.user.provider_ids.filtered(lambda x: x.company_id == self.env.company)
        # provider_channel_id = self.partner_id.channel_provider_line_ids.filtered(
        #     lambda s: s.provider_id == self.env.user.provider_id)
        provider_channel_id = self.partner_id.channel_provider_line_ids.filtered(
            lambda s: s.provider_id == provider_id)
        effect = False
        if provider_channel_id:
            channel = provider_channel_id.channel_id
            if user_partner.id not in channel.channel_partner_ids.ids and self.env.user.has_group('base.group_user') and self.env.user.has_group('tus_meta_whatsapp_base.whatsapp_group_user'):
                channel.sudo().write({'channel_partner_ids': [(4, user_partner.id)]})
                mail_channel_partner = self.env['mail.channel.partner'].sudo().search(
                    [('channel_id', '=', channel.id),
                     ('partner_id', '=', user_partner.id)])
                mail_channel_partner.sudo().write({'is_pinned': True})
                effect = {'effect': {'fadeout': 'slow',
                           'message': "You have added in this customer chat Now.",
                           }
                }
        else:
            name = self.partner_id.mobile
            channel = self.env['mail.channel'].create({
                'public': 'public',
                'channel_type': 'chat',
                'name': name,
                'whatsapp_channel': True,
                'channel_partner_ids': [(4,self.partner_id.id)],
            })
            channel.write({'channel_last_seen_partner_ids': [(5, 0, 0)] + [
                (0, 0, {'partner_id': line_vals}) for line_vals in part_lst]})
            # Multi Companies and Multi Providers Code Here
            # self.partner_id.write({'channel_provider_line_ids': [
            #     (0, 0, {'channel_id': channel.id, 'provider_id': self.env.user.provider_id.id})]})
            self.partner_id.write({'channel_provider_line_ids': [
                (0, 0, {'channel_id': channel.id, 'provider_id': provider_id.id})]})

        if channel:
            if self.template_id:
                wa_message_values = {}
                if self.body != '':
                    wa_message_values.update({'body': tools.html2plaintext(self.body)})
                if self.attachment_ids:
                    wa_message_values.update({'attachment_ids': [(4, attac_id.id) for attac_id in self.attachment_ids]})
                wa_message_values.update({
                    'author_id': user_partner.id,
                    'email_from': user_partner.email or '',
                    'model': 'mail.channel',
                    'message_type': 'wa_msgs',
                    'isWaMsgs': True,
                    'subtype_id': self.env['ir.model.data'].sudo()._xmlid_to_res_id('mail.mt_comment'),
                    # 'channel_ids': [(4, channel.id)],
                    'partner_ids': [(4, user_partner.id)],
                    'res_id': channel.id,
                    'reply_to': user_partner.email,
                })
                wa_attach_message = self.env['mail.message'].sudo().with_context(
                    {'template_send': True, 'wa_template': self.template_id, 'active_model_id': active_id, 'active_model': active_model,
                     'attachment_ids': self.attachment_ids.ids, 'provider_id': provider_id}).create(
                    wa_message_values)
                notifications = channel._channel_message_notifications(wa_attach_message)
                self.env['bus.bus']._sendmany(notifications)

                message_values = {
                    'body': self.body,
                    'author_id': user_partner.id,
                    'email_from': user_partner.email or '',
                    'model': active_model,
                    'message_type': 'comment',
                    'isWaMsgs': True,
                    'subtype_id': self.env['ir.model.data'].sudo()._xmlid_to_res_id('mail.mt_comment'),
                    # 'channel_ids': [(4, channel.id)],
                    'partner_ids': [(4, user_partner.id)],
                    'res_id': record.id,
                    'reply_to': user_partner.email,
                    'attachment_ids': [(4, attac_id.id) for attac_id in self.attachment_ids],
                }
                if self.attachment_ids:
                    message_values.update({})
                message = self.env['mail.message'].sudo().with_context({'provider_id': self.provider_id}).create(
                    message_values)
                wa_attach_message.chatter_wa_model = active_model
                wa_attach_message.chatter_wa_res_id = record.id
                wa_attach_message.chatter_wa_message_id = message.id
                notifications = channel._channel_message_notifications(message)
                self.env['bus.bus']._sendmany(notifications)
            else:
                if tools.html2plaintext(self.body) != '':
                    message_values = {
                        'body': tools.html2plaintext(self.body),
                        'author_id': user_partner.id,
                        'email_from': user_partner.email or '',
                        'model': 'mail.channel',
                        'message_type': 'wa_msgs',
                        'isWaMsgs': True,
                        'subtype_id': self.env['ir.model.data'].sudo()._xmlid_to_res_id('mail.mt_comment'),
                        # 'channel_ids': [(4, channel.id)],
                        'partner_ids': [(4, user_partner.id)],
                        'res_id': channel.id,
                        'reply_to': user_partner.email,
                    }
                    if self.template_id:
                        wa_message_body = self.env['mail.message'].sudo().with_context({'template_send': True, 'wa_template': self.template_id,'active_model_id': active_id, 'active_model': active_model, 'provider_id': self.provider_id}).create(
                            message_values)
                    else:
                        wa_message_body = self.env['mail.message'].sudo().with_context({'provider_id': self.provider_id}).create(
                            message_values)
                    notifications = channel._channel_message_notifications(wa_message_body)
                    self.env['bus.bus']._sendmany(notifications)

                    message_values = {
                        'body': self.body,
                        'author_id': user_partner.id,
                        'email_from': user_partner.email or '',
                        'model': active_model,
                        'message_type': 'comment',
                        'isWaMsgs': True,
                        'subtype_id': self.env['ir.model.data'].sudo()._xmlid_to_res_id('mail.mt_comment'),
                        # 'channel_ids': [(4, channel.id)],
                        'partner_ids': [(4, user_partner.id)],
                        'res_id': record.id,
                        'reply_to': user_partner.email,
                    }
                    message = self.env['mail.message'].sudo().with_context({'provider_id': self.provider_id}).create(
                        message_values)
                    wa_message_body.chatter_wa_model = active_model
                    wa_message_body.chatter_wa_res_id = record.id
                    wa_message_body.chatter_wa_message_id = message.id
                    notifications = channel._channel_message_notifications(message)
                    self.env['bus.bus']._sendmany(notifications)

                if self.attachment_ids:
                    message_values = {
                        'body':'',
                        'author_id': user_partner.id,
                        'email_from': user_partner.email or '',
                        'model': 'mail.channel',
                        'message_type': 'wa_msgs',
                        'isWaMsgs': True,
                        'subtype_id': self.env['ir.model.data'].sudo()._xmlid_to_res_id('mail.mt_comment'),
                        # 'channel_ids': [(4, channel.id)],
                        'partner_ids': [(4, user_partner.id)],
                        'res_id': channel.id,
                        'reply_to': user_partner.email,
                        'attachment_ids': [(4, attac_id.id) for attac_id in self.attachment_ids],
                    }
                    if self.template_id:
                        wa_attach_message = self.env['mail.message'].sudo().with_context({'template_send': True, 'wa_template': self.template_id, 'active_model_id': active_id, 'active_model': active_model, 'attachment_ids': self.attachment_ids.ids, 'provider_id': self.provider_id}).create(
                            message_values)
                    else:
                        wa_attach_message = self.env['mail.message'].sudo().with_context({'provider_id': self.provider_id}).create(
                            message_values)
                    # wa_attach_message = self.env['mail.message'].sudo().create(
                    #     message_values)
                    notifications = channel._channel_message_notifications(wa_attach_message)
                    self.env['bus.bus']._sendmany(notifications)

                    message_values = {
                        'author_id': user_partner.id,
                        'email_from': user_partner.email or '',
                        'model': active_model,
                        'message_type': 'comment',
                        'isWaMsgs': True,
                        'subtype_id': self.env['ir.model.data'].sudo()._xmlid_to_res_id('mail.mt_comment'),
                        # 'channel_ids': [(4, channel.id)],
                        'partner_ids': [(4, user_partner.id)],
                        'res_id': record.id,
                        'reply_to': user_partner.email,
                        'attachment_ids': [(4, attac_id.id) for attac_id in self.attachment_ids],
                    }
                    if self.attachment_ids:
                        message_values.update({})
                    message = self.env['mail.message'].sudo().with_context({'provider_id': self.provider_id}).create(
                        message_values)
                    wa_attach_message.chatter_wa_model = active_model
                    wa_attach_message.chatter_wa_res_id = record.id
                    wa_attach_message.chatter_wa_message_id = message.id
                    notifications = channel._channel_message_notifications(message)
                    self.env['bus.bus']._sendmany(notifications)
        if effect:
            return effect







