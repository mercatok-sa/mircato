from odoo.http import request
from odoo import http, _, tools
import requests
import json
import base64
import phonenumbers
import datetime
from odoo.exceptions import UserError, ValidationError
from phonenumbers.phonenumberutil import (
    region_code_for_country_code,
)
import hashlib
import base64


class WebHookMeta(http.Controller):
    _webhook_url = '/graph_tus/webhook'
    _meta_fb_url = '/graph_tus/webhook'

    # @http.route(['/graph_tus/webhook'], auth='public', type="http", csrf=False, methods=['GET'])
    @http.route(_webhook_url, type='http', methods=['GET'], auth='public', csrf=False)
    def facebook_webhook(self, **kw):
        #print("1111111111111111111 main*********************facebook_webhook", self, kw)
        if kw.get('hub.verify_token'):
            return kw.get('hub.challenge')

    def get_channel(self, partner_to, provider):
        partner = False
        if len(partner_to) > 0:
            partner = request.env['res.partner'].sudo().browse(partner_to[0])
        if request.env.user.has_group('base.group_user'):
            partner_to.append(request.env.user.partner_id.id)
        else:
            partner_to.append(provider.user_id.partner_id.id)
        channel = False

        provider_channel_id = partner.channel_provider_line_ids.filtered(lambda s: s.provider_id == provider)
        if provider_channel_id:
            channel = provider_channel_id.channel_id
            if request.env.user.partner_id.id not in channel.channel_partner_ids.ids and request.env.user.has_group(
                    'base.group_user'):
                channel.sudo().write({'channel_partner_ids': [(4, request.env.user.partner_id.id)]})
        else:
            # phone change to mobile
            name = partner.mobile
            channel = request.env['mail.channel'].sudo().create({
                'public': 'public',
                'channel_type': 'chat',
                'name': name,
                'whatsapp_channel': True,
                'channel_partner_ids': [(4, x) for x in partner_to],
            })
            channel.write({'channel_last_seen_partner_ids': [(5, 0, 0)] + [
                (0, 0, {'partner_id': line_vals}) for line_vals in partner_to]})
            # partner.write({'channel_id': channel.id})
            partner.write({'channel_provider_line_ids': [
                (0, 0, {'channel_id': channel.id, 'provider_id': provider.id})]})
        return channel

    def get_url(self, provider, media_id, phone_number_id):
        if provider.graph_api_authenticated:
            url = provider.graph_api_url + media_id + "?phone_number_id=" + phone_number_id + "&access_token=" + provider.graph_api_token
            headers = {'Content-type': 'application/json'}
            payload = {}
            try:
                answer = requests.request("GET", url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def get_media_data(self, url, provider):
        payload = {}
        headers = {
            'Authorization': 'Bearer ' + provider.graph_api_token
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        decoded = base64.b64encode(response.content)
        return decoded

    # @http.route(['/graph_tus/webhook'], auth='public', type="json", csrf=False, methods=['GET', 'POST'])
    @http.route(_meta_fb_url, type='json', methods=['GET', 'POST'], auth='public', csrf=False)
    def meta_webhook(self, **kw):
        #print("2222222222222222222 main*********************meta_webhook", self, kw)
        wa_dict = {}
        
        data = json.loads(request.httprequest.data.decode('utf-8'))
        wa_dict.update({'messages': data.get('messages')})

        phone_number_id = ''
        if data and data.get('entry'):
            if data.get('entry')[0].get('changes'):
                if data.get('entry')[0].get('changes')[0].get('value'):
                    if data.get('entry')[0].get('changes')[0].get('value').get('metadata'):
                        if data.get('entry')[0].get('changes')[0].get('value').get('metadata').get('phone_number_id'):
                            phone_number_id = data.get('entry')[0].get('changes')[0].get('value').get('metadata').get(
                                'phone_number_id')

        provider = request.env['provider'].sudo().search(
            [('graph_api_authenticated', '=', True), ('graph_api_instance_id', '=', phone_number_id)], limit=1)
        wa_dict.update({'provider': provider})
        #user_partner = provider.user_id.partner_id
        #channel = self.get_channel([int(user_partner.id)], provider)

        if data and data.get('entry'):
            if data.get('entry')[0].get('changes'):
                if data.get('entry')[0].get('changes')[0].get('value'):
                    if data.get('entry')[0].get('changes')[0].get('value').get('statuses'):
                        for acknowledgment in data.get('entry')[0].get('changes')[0].get('value').get('statuses'):
                            wp_msgs = request.env['whatsapp.history'].sudo().search(
                                [('message_id', '=', acknowledgment.get('id'))], limit=1)
                            if wp_msgs:
                                partner = request.env['res.partner'].sudo().search(
                                    ['|', ('phone', '=', acknowledgment.get('recipient_id')),
                                     ('mobile', '=', acknowledgment.get('recipient_id'))], limit=1)
                                channel = self.get_channel([int(partner.id)], provider)
                                wa_mail_message = request.env['mail.message'].sudo().search(
                                    [('wa_message_id', '=', acknowledgment.get('id'))], limit=1)
                                if acknowledgment.get('status') == 'sent':
                                    wp_msgs.sudo().write({'type': 'sent'})
                                    wa_mail_message.write({'wp_status': acknowledgment.get('status')})
                                    notifications = channel._channel_message_notifications(wa_mail_message)
                                    request.env['bus.bus']._sendmany(notifications)
                                elif acknowledgment.get('status') == 'delivered':
                                    wp_msgs.sudo().write({'type': 'delivered'})
                                    wa_mail_message.write({'wp_status': acknowledgment.get('status')})
                                    notifications = channel._channel_message_notifications(wa_mail_message)
                                    request.env['bus.bus']._sendmany(notifications)
                                elif acknowledgment.get('status') == 'read':
                                    wp_msgs.sudo().write({'type': 'read'})
                                    wa_mail_message.write({'wp_status': acknowledgment.get('status')})
                                    notifications = channel._channel_message_notifications(wa_mail_message)
                                    request.env['bus.bus']._sendmany(notifications)
                                elif acknowledgment.get('status') == 'failed':
                                    wp_msgs.sudo().write(
                                        {'type': 'fail', 'fail_reason': acknowledgment.get('errors')[0].get('title')})
                                    wa_mail_message.write({'wp_status': 'fail',
                                                           'wa_delivery_status': acknowledgment.get('status'),
                                                           'wa_error_message': acknowledgment.get('errors')[0].get(
                                                               'error_data').get('details')})
                                    notifications = channel._channel_message_notifications(wa_mail_message)
                                    request.env['bus.bus']._sendmany(notifications)

        if provider.graph_api_authenticated:
            user_partner = provider.user_id.partner_id
            if data and data.get('entry'):
                if data.get('entry')[0].get('changes'):
                    if data.get('entry')[0].get('changes')[0].get('value'):
                        if data.get('entry')[0].get('changes')[0].get('value').get('messages'):
                            for mes in data.get('entry')[0].get('changes')[0].get('value').get('messages'):
                                number = mes.get('from')
                                messages_id = mes.get('id')
                                # messages_body = mes.get('text').get('body')
                                wa_dict.update({'chat': True})
                                partners = request.env['res.partner'].sudo().search(
                                    ['|', ('phone', '=', number), ('mobile', '=', number)])
                                wa_dict.update({'partners': partners})
                                if not partners:
                                    pn = phonenumbers.parse('+' + number)
                                    country_code = region_code_for_country_code(pn.country_code)
                                    country_id = request.env['res.country'].sudo().search(
                                        [('code', '=', country_code)], limit=1)
                                    partners = request.env['res.partner'].sudo().create(
                                        {'name': data.get('entry')[0].get('changes')[0].get('value').get('contacts')[
                                            0].get('profile').get('name'), 'country_id': country_id.id,
                                         'mobile': number})

                                for partner in partners:
                                    partner_id = partner.id
                                    # channel = self.get_channel([int(partner_id)], provider)
                                    if mes.get('type') == 'text':
                                        vals = {
                                            'provider_id': provider.id,
                                            'author_id': user_partner.id,
                                            'message': mes.get('text').get('body'),
                                            'message_id': messages_id,
                                            'type': 'received',
                                            'partner_id': partner_id,
                                            'phone': partner.mobile,
                                            'attachment_ids': False,
                                            'company_id': provider.company_id.id,
                                            # 'date':datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                        }
                                        if 'context' in mes:
                                            request.env['whatsapp.history'].sudo().with_context(
                                                {'quotedMsgId': mes.get('context').get('id')}).create(vals)
                                        else:
                                            request.env['whatsapp.history'].sudo().create(vals)

                                    elif mes.get('type') == 'location':
                                        # phone change to mobile
                                        lat = mes.get('location').get('latitude')
                                        lag = mes.get('location').get('longitude')
                                        vals = {
                                            'message': "<a href='https://www.google.com/maps/search/?api=1&query=" + str(
                                                lat) + "," + str(
                                                lag) + "' target='_blank' class='btn btn-primary'>Google Map</a>",
                                            'message_id': messages_id,
                                            'author_id': user_partner.id,
                                            'type': 'received',
                                            'partner_id': partner_id,
                                            'phone': partner.mobile,
                                            'attachment_ids': False,
                                            'provider_id': provider.id,
                                            'company_id': provider.company_id.id,
                                            # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                        }
                                        if 'context' in mes:
                                            request.env['whatsapp.history'].sudo().with_context(
                                                {'quotedMsgId': mes.get('context').get('id')}).create(vals)
                                        else:
                                            request.env['whatsapp.history'].sudo().create(vals)
                                    elif mes.get('type') == 'image':
                                        media_id = mes.get('image').get('id')
                                        geturl = self.get_url(provider, media_id, phone_number_id)
                                        dict = json.loads(geturl.text)
                                        decoded = self.get_media_data(dict.get('url'), provider)

                                        attachment_value = {
                                            'name': mes.get('image').get('id'),
                                            'datas': decoded,
                                            'type': 'binary',
                                            'mimetype': mes.get('image').get('mime_type') if mes.get(
                                                'image') and mes.get('image').get('mime_type') else 'image/jpeg',
                                        }
                                        attachment = request.env['ir.attachment'].sudo().create(attachment_value)
                                        if 'context' in mes:
                                            request.env['whatsapp.history'].sudo().with_context(
                                                {'quotedMsgId': mes.get('context').get('id')}).create(
                                                {'message': mes.get('image').get(
                                                    'caption') if 'image' in mes and 'caption' in mes.get(
                                                    'image') else '',
                                                 'message_id': messages_id,
                                                 'author_id': user_partner.id,
                                                 'type': 'received',
                                                 'partner_id': partner_id,
                                                 'phone': partner.mobile,
                                                 'attachment_ids': [(4, attachment.id)],
                                                 'provider_id': provider.id,
                                                 'company_id': provider.company_id.id,
                                                 # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                                 })
                                        else:
                                            res = request.env['whatsapp.history'].sudo().create(
                                                {'message': mes.get('image').get(
                                                    'caption') if 'image' in mes and 'caption' in mes.get(
                                                    'image') else '',
                                                 'message_id': messages_id,
                                                 'author_id': user_partner.id,
                                                 'type': 'received',
                                                 'partner_id': partner_id,
                                                 'phone': partner.mobile,
                                                 'attachment_ids': [(4, attachment.id)],
                                                 'provider_id': provider.id,
                                                 'company_id': provider.company_id.id,
                                                 # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                                 })
                                    elif mes.get('type') == 'document':
                                        media_id = mes.get('document').get('id')
                                        geturl = self.get_url(provider, media_id, phone_number_id)
                                        dict = json.loads(geturl.text)
                                        decoded = self.get_media_data(dict.get('url'), provider)

                                        attachment_value = {
                                            'name': mes.get('document').get('filename'),
                                            'datas': decoded,
                                            'type': 'binary',
                                            'mimetype': mes.get('document').get('mime_type') if mes.get(
                                                'document') and mes.get('document').get(
                                                'mime_type') else 'application/pdf',
                                        }
                                        attachment = request.env['ir.attachment'].sudo().create(attachment_value)
                                        if 'context' in mes:
                                            request.env['whatsapp.history'].sudo().with_context(
                                                {'quotedMsgId': mes.get('context').get('id')}).create(
                                                {'message': mes.get('document').get(
                                                    'caption') if 'document' in mes and 'caption' in mes.get(
                                                    'document') else '',
                                                 'message_id': messages_id,
                                                 'author_id': user_partner.id,
                                                 'type': 'received',
                                                 'partner_id': partner_id,
                                                 'phone': partner.mobile,
                                                 'attachment_ids': [(4, attachment.id)],
                                                 'provider_id': provider.id,
                                                 'company_id': provider.company_id.id,
                                                 # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                                 })
                                        else:
                                            res = request.env['whatsapp.history'].sudo().create(
                                                {'message': mes.get('document').get(
                                                    'caption') if 'document' in mes and 'caption' in mes.get(
                                                    'document') else '',
                                                 'message_id': messages_id,
                                                 'author_id': user_partner.id,
                                                 'type': 'received',
                                                 'partner_id': partner_id,
                                                 'phone': partner.mobile,
                                                 'attachment_ids': [(4, attachment.id)],
                                                 'provider_id': provider.id,
                                                 'company_id': provider.company_id.id,
                                                 # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                                 })
                                    elif mes.get('type') == 'video':
                                        media_id = mes.get('video').get('id')
                                        geturl = self.get_url(provider, media_id, phone_number_id)
                                        dict = json.loads(geturl.text)
                                        decoded = self.get_media_data(dict.get('url'), provider)

                                        attachment_value = {
                                            'name': 'whatsapp_video',
                                            'datas': decoded,
                                            'type': 'binary',
                                            'mimetype': mes.get('video').get('mime_type') if mes.get(
                                                'video') and mes.get('video').get('mime_type') else 'video/mp4',
                                        }
                                        attachment = request.env['ir.attachment'].sudo().create(attachment_value)
                                        if 'context' in mes:
                                            request.env['whatsapp.history'].sudo().with_context(
                                                {'quotedMsgId': mes.get('context').get('id')}).create(
                                                {'message': mes.get('video').get(
                                                    'caption') if 'video' in mes and 'caption' in mes.get(
                                                    'video') else '',
                                                 'message_id': messages_id,
                                                 'author_id': user_partner.id,
                                                 'type': 'received',
                                                 'partner_id': partner_id,
                                                 'phone': partner.mobile,
                                                 'attachment_ids': [(4, attachment.id)],
                                                 'provider_id': provider.id,
                                                 'company_id': provider.company_id.id,
                                                 # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                                 })
                                        else:
                                            res = request.env['whatsapp.history'].sudo().create(
                                                {'message': mes.get('video').get(
                                                    'caption') if 'video' in mes and 'caption' in mes.get(
                                                    'video') else '',
                                                 'message_id': messages_id,
                                                 'author_id': user_partner.id,
                                                 'type': 'received',
                                                 'partner_id': partner_id,
                                                 'phone': partner.mobile,
                                                 'attachment_ids': [(4, attachment.id)],
                                                 'provider_id': provider.id,
                                                 'company_id': provider.company_id.id,
                                                 # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                                 })
                                    elif mes.get('type') == 'audio':
                                        media_id = mes.get('audio').get('id')
                                        geturl = self.get_url(provider, media_id, phone_number_id)
                                        dict = json.loads(geturl.text)
                                        decoded = self.get_media_data(dict.get('url'), provider)

                                        attachment_value = {
                                            'name': 'whatsapp_audio',
                                            'datas': decoded,
                                            'type': 'binary',
                                            'mimetype': mes.get('audio').get('mime_type') if mes.get(
                                                'audio') and mes.get('audio').get('mime_type') else 'audio/mpeg',
                                        }
                                        attachment = request.env['ir.attachment'].sudo().create(attachment_value)
                                        if 'context' in mes:
                                            request.env['whatsapp.history'].sudo().with_context(
                                                {'quotedMsgId': mes.get('context').get('id')}).create(
                                                {'message': mes.get('audio').get(
                                                    'caption') if 'audio' in mes and 'caption' in mes.get(
                                                    'audio') else '',
                                                 'message_id': messages_id,
                                                 'author_id': user_partner.id,
                                                 'type': 'received',
                                                 'partner_id': partner_id,
                                                 'phone': partner.mobile,
                                                 'attachment_ids': [(4, attachment.id)],
                                                 'provider_id': provider.id,
                                                 'company_id': provider.company_id.id,
                                                 # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                                 })
                                        else:
                                            res = request.env['whatsapp.history'].sudo().create(
                                                {'message': mes.get('audio').get(
                                                    'caption') if 'audio' in mes and 'caption' in mes.get(
                                                    'audio') else '',
                                                 'message_id': messages_id,
                                                 'author_id': user_partner.id,
                                                 'type': 'received',
                                                 'partner_id': partner_id,
                                                 'phone': partner.mobile,
                                                 'attachment_ids': [(4, attachment.id)],
                                                 'provider_id': provider.id,
                                                 'company_id': provider.company_id.id,
                                                 # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                                 })
                                    elif mes.get('type') == 'sticker':
                                        media_id = mes.get('sticker').get('id')
                                        geturl = self.get_url(provider, media_id, phone_number_id)
                                        dict = json.loads(geturl.text)
                                        decoded = self.get_media_data(dict.get('url'), provider)

                                        attachment_value = {
                                            'name': 'whatsapp_sticker',
                                            'datas': decoded,
                                            'type': 'binary',
                                            'mimetype': mes.get('sticker').get('mime_type') if mes.get(
                                                'sticker') and mes.get('sticker').get('mime_type') else 'image/webp',
                                        }
                                        attachment = request.env['ir.attachment'].sudo().create(attachment_value)
                                        if 'context' in mes:
                                            request.env['whatsapp.history'].sudo().with_context(
                                                {'quotedMsgId': mes.get('context').get('id')}).create(
                                                {'message': mes.get('sticker').get(
                                                    'caption') if 'sticker' in mes and 'caption' in mes.get(
                                                    'sticker') else '',
                                                 'message_id': messages_id,
                                                 'author_id': user_partner.id,
                                                 'type': 'received',
                                                 'partner_id': partner_id,
                                                 'phone': partner.mobile,
                                                 'attachment_ids': [(4, attachment.id)],
                                                 'provider_id': provider.id,
                                                 'company_id': provider.company_id.id,
                                                 # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                                 })
                                        else:
                                            res = request.env['whatsapp.history'].sudo().create(
                                                {'message': mes.get('sticker').get(
                                                    'caption') if 'sticker' in mes and 'caption' in mes.get(
                                                    'sticker') else '',
                                                 'message_id': messages_id,
                                                 'author_id': user_partner.id,
                                                 'type': 'received',
                                                 'partner_id': partner_id,
                                                 'phone': partner.mobile,
                                                 'attachment_ids': [(4, attachment.id)],
                                                 'provider_id': provider.id,
                                                 'company_id': provider.company_id.id,
                                                 # 'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                                 })
                                    elif mes.get('type') == 'reaction':
                                        vals = {
                                            'provider_id': provider.id,
                                            'author_id': user_partner.id,
                                            'message': mes.get('reaction').get('emoji'),
                                            'message_id': messages_id,
                                            'type': 'received',
                                            'partner_id': partner_id,
                                            'phone': partner.mobile,
                                            'attachment_ids': False,
                                            'company_id': provider.company_id.id,
                                            # 'date':datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                        }
                                        if mes.get('reaction', {}).get('message_id', False):
                                            request.env['whatsapp.history'].sudo().with_context(
                                                {'quotedMsgId': mes.get('reaction').get('message_id')}).create(vals)
                                        else:
                                            request.env['whatsapp.history'].sudo().create(vals)
                                    elif mes.get('type') == 'button':
                                        vals = {
                                            'provider_id': provider.id,
                                            'author_id': user_partner.id,
                                            'message': mes.get('button').get('text'),
                                            'message_id': messages_id,
                                            'type': 'received',
                                            'partner_id': partner_id,
                                            'phone': partner.mobile,
                                            'attachment_ids': False,
                                            'company_id': provider.company_id.id,
                                            # 'date':datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                        }
                                        if 'context' in mes:
                                            request.env['whatsapp.history'].sudo().with_context(
                                                {'quotedMsgId': mes.get('context').get('id')}).create(vals)
                                        else:
                                            request.env['whatsapp.history'].sudo().create(vals)
                                    elif mes.get('type') == 'interactive':
                                        title = list(
                                            map(lambda l: mes.get('interactive').get(l), mes.get('interactive')))
                                        vals = {
                                            'provider_id': provider.id,
                                            'author_id': user_partner.id,
                                            'message': len(title) > 0 and title[1].get('title') or '',
                                            'message_id': messages_id,
                                            'type': 'received',
                                            'partner_id': partner_id,
                                            'phone': partner.mobile,
                                            'attachment_ids': False,
                                            'company_id': provider.company_id.id,
                                            # 'date':datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                        }
                                        if 'context' in mes:
                                            request.env['whatsapp.history'].sudo().with_context(
                                                {'quotedMsgId': mes.get('context').get('id')}).create(vals)
                                        else:
                                            request.env['whatsapp.history'].sudo().create(vals)
                                    else:
                                        vals = {
                                            'provider_id': provider.id,
                                            'author_id': user_partner.id,
                                            'message': mes.get('text').get('body'),
                                            'message_id': messages_id,
                                            'type': 'received',
                                            'partner_id': partner_id,
                                            'phone': partner.mobile,
                                            'attachment_ids': False,
                                            'company_id': provider.company_id.id,
                                            # 'date':datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                        }
                                        request.env['whatsapp.history'].sudo().create(vals)
        return wa_dict

    @http.route(['/send/product'], type='json', methods=['POST'])
    def _send_product_by_whatsapp(self, **kw):
        provider_id = False
        if 'provider_id' in kw and kw.get('provider_id') != '':
            channel_company_line_id = request.env['channel.provider.line'].search(
                [('channel_id', '=', kw.get('provider_id'))])
            if channel_company_line_id.provider_id:
                provider_id = channel_company_line_id.provider_id

        # image = kw.get('image').split(',')[1]
        Attachment = request.env['ir.attachment']
        partner_id = request.env['res.partner'].sudo().browse(int(kw.get('partner_id')))
        product = request.env['product.product'].sudo().browse(int(kw.get('product_id')))
        body_message = product.name + "\n" + request.env.user.company_id.currency_id.symbol + " " + str(
            product.list_price) + " / " + product.uom_id.name
        attac_id = False
        if product.image_1920:
            name = product.name + '.png'
            attac_id = request.env['ir.attachment'].sudo().search([('name', '=', name)], limit=1)
            if not attac_id:
                attac_id = Attachment.create({'name': name,
                                              'type': 'binary',
                                              'datas': product.image_1920,
                                              'store_fname': name,
                                              'res_model': 'wa.msgs',
                                              'mimetype': 'image/jpeg',
                                              })
        user_partner = request.env.user.partner_id
        channel = self.get_channel([int(kw.get('partner_id'))], provider_id)

        if channel:
            message_values = {
                'body': body_message,
                'author_id': user_partner.id,
                'email_from': user_partner.email or '',
                'model': 'mail.channel',
                'message_type': 'wa_msgs',
                'isWaMsgs': True,
                # 'subtype_id': request.env['ir.model.data'].sudo().xmlid_to_res_id('mail.mt_comment'),
                'subtype_id': request.env['ir.model.data'].sudo()._xmlid_to_res_id('mail.mt_comment'),
                # 'channel_ids': [(4, channel.id)],
                'partner_ids': [(4, user_partner.id)],
                'res_id': channel.id,
                'reply_to': user_partner.email,
                # 'company_id': kw.get('company_id'),
            }
            if attac_id:
                message_values.update({'attachment_ids': [(4, attac_id.id)]})
            message = request.env['mail.message'].sudo().with_context({'provider_id': provider_id}).create(
                message_values)
            notifications = channel._channel_message_notifications(message)
            request.env['bus.bus']._sendmany(notifications)

        return True

    @http.route(['/send/pre/message'], type='json', methods=['POST'])
    def _send_pre_message_by_whatsapp(self, **kw):
        template_id = request.env['wa.template'].sudo().browse(int(kw.get('template_id')))
        active_model = template_id.model
        provider_id = template_id.provider_id
        wizard_rec = request.env['wa.compose.message'].with_context(active_model=active_model,
                                                                    active_id=int(kw.get('partner_id'))).create(
            {'partner_id': int(kw.get('partner_id')), 'provider_id': provider_id.id,
             'template_id': int(kw.get('template_id'))})
        wizard_rec.onchange_template_id_wrapper()
        return wizard_rec.send_whatsapp_message()
        # if wizard open
        # context = {'active_model':active_model,'active_id':int(kw.get('partner_id')),'default_partner_id':int(kw.get('partner_id')),'default_provider_id':int(kw.get('template_id'))}
        # action = request.env.ref('tus_meta_whatsapp_base.action_wa_compose_message_wizard').read()[0]
        # action['context'] = context
        # return action
