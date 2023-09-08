from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.addons.tus_meta_whatsapp_base.controllers.main_meta import WebHookMeta
from odoo.http import request

class WebHookExt(WebHookMeta):

    @http.route(['/get/template/content'], auth='public', type='json', website=True, methods=['POST', 'GET'])
    def get_template_content(self, **kw):
        template_id = False
        if kw.get('template_id') != '':
            template_id = request.env['wa.template'].sudo().browse(int(kw.get('template_id')))
        pos_order_id = request.env['pos.order'].sudo().search([('pos_reference', '=', kw.get('order_name'))])
        if template_id and pos_order_id:
            body = template_id._render_field('body_html', [pos_order_id.id], compute_lang=True)[
                pos_order_id.id]
            body = tools.html2plaintext(body)
            return body
        else:
            return False

    @http.route(['/send/receipt'], auth='public', type='json', website=True, methods=['POST'])
    def send_receipt_by_whatsapp(self, **kw):
        image = kw.get('image')
        Attachment = request.env['ir.attachment']
        partner_id = request.env['res.partner'].sudo().browse(int(kw.get('id')))
        pos_order_id = request.env['pos.order'].sudo().search([('pos_reference', '=', kw.get('receipt_name'))])
        provider_id = False
        template = False
        if 'provider' in kw and kw.get('provider') != '':
            provider_id = request.env['provider'].sudo().browse(int(kw.get('provider')))
        if 'template' in kw and kw.get('template') != '':
            template = request.env['wa.template'].sudo().browse(int(kw.get('template')))
        name = kw.get('receipt_name')
        filename = 'Receipt-' + name + '.jpg'
        attac_id = Attachment.sudo().search([('name', '=', filename)], limit=1)
        if not attac_id:
            attac_id = Attachment.create({
                'name': filename,
                'type': 'binary',
                'datas': image,
                'res_model': 'wa.msgs',
                'store_fname': filename,
                'mimetype': 'image/jpeg',
            })
        user_partner = request.env.user.partner_id
        # Multi Companies and Multi Providers Code Here
        # provider_id = request.env.user.provider_ids.filtered(lambda x: x.company_id == request.env.company)
        channel = self.get_channel([int(kw.get('id'))], provider_id)

        if channel:
            if template:
                message_values = {
                    'body': kw.get('message'),
                    'author_id': user_partner.id,
                    'email_from': user_partner.email or '',
                    'model': 'mail.channel',
                    'message_type': 'wa_msgs',
                    # 'isWaMsgs': True,
                    'subtype_id': request.env['ir.model.data'].sudo()._xmlid_to_res_id('mail.mt_comment'),
                    # 'channel_ids': [(4, channel.id)],
                    'partner_ids': [(4, user_partner.id)],
                    'res_id': channel.id,
                    'reply_to': user_partner.email,
                }
                if attac_id:
                    message_values.update({'attachment_ids': [(4, attac_id.id)]})

                try:
                    wa_attach_message = request.env['mail.message'].sudo().with_context(
                        {'template_send': True, 'wa_template': template, 'active_model_id': pos_order_id.id,
                         'attachment_ids': attac_id.ids, 'provider_id': provider_id}).create(
                        message_values)
                except:
                    return {'error':'template_name does not exist. Please try after sometime!'}

                notifications = channel._channel_message_notifications(wa_attach_message)
                request.env['bus.bus']._sendmany(notifications)

                message_values = {
                    'body': kw.get('message'),
                    'author_id': user_partner.id,
                    'email_from': user_partner.email or '',
                    'model': 'pos.order',
                    'message_type': 'comment',
                    'isWaMsgs': True,
                    'subtype_id': request.env['ir.model.data'].sudo()._xmlid_to_res_id('mail.mt_comment'),
                    # 'channel_ids': [(4, channel.id)],
                    'partner_ids': [(4, user_partner.id)],
                    'res_id': pos_order_id.id,
                    'reply_to': user_partner.email,
                    'attachment_ids': [(4, attac_id.id)],
                }

                message = request.env['mail.message'].sudo().with_context(
                    {'provider_id': provider_id}).create(message_values)
                wa_attach_message.chatter_wa_model = 'pos.order'
                wa_attach_message.chatter_wa_res_id = pos_order_id.id
                wa_attach_message.chatter_wa_message_id = message.id
                notifications = channel._channel_message_notifications(message)
                request.env['bus.bus']._sendmany(notifications)
        return True
