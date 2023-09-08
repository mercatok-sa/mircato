from odoo.http import request
from odoo import http,_,tools
import requests
import json
import base64
import phonenumbers
import datetime
from odoo.exceptions import UserError, ValidationError
from phonenumbers.phonenumberutil import (
    region_code_for_country_code,
)

class WebHook(http.Controller):

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

    @http.route(['/chat_api/webhook'], auth='public', type="json", csrf=False, methods=['GET', 'POST'])
    def whatsapp_webhook(self, **kw):
        # print("111 main*********************whatsapp_webhook", self, kw)
        wa_dict = {}
        data = json.loads(request.httprequest.data.decode('utf-8'))

        wa_dict.update({'messages': data.get('messages')})

        provider = request.env['provider'].sudo().search([('chat_api_instance_id', '=', data.get('instanceId'))], limit=1)
        wa_dict.update({'provider': provider})

        if 'ack' in data and data.get('ack'):
            for acknowledgment in data.get('ack'):
                wp_msgs = request.env['whatsapp.history'].sudo().search(
                    [('message_id', '=', acknowledgment.get('id'))], limit=1)
                if wp_msgs:
                    if acknowledgment.get('status') == 'sent':
                        wp_msgs.sudo().write({'type': 'sent'})
                    elif acknowledgment.get('status') == 'delivered':
                        wp_msgs.sudo().write({'type': 'delivered'})
                    elif acknowledgment.get('status') == 'read':
                        wp_msgs.sudo().write({'type': 'read'})

        if provider.chat_api_authenticated:
            user_partner = provider.user_id.partner_id
            if 'messages' in data and data.get('messages'):
                for mes in data.get('messages'):
                    phone_no = mes.get('author').split('@')
                    chat_number = mes.get('chatId').split('@')
                    number = chat_number[0].strip('+').replace(" ", "")
                    if chat_number[1] == 'c.us':
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
                                {'name': mes['chatName'], 'country_id': country_id.id, 'mobile': number})
                        for partner in partners:
                            partner_id = partner.id
                            if mes.get('self') == 0:
                                # phone change to mobile
                                if mes['type'] == 'chat':
                                    vals = {
                                            'provider_id':provider.id,
                                            'author_id':user_partner.id,
                                            'message': mes.get('body'),
                                            'message_id': mes.get('id'),
                                            'type': 'received',
                                            'partner_id': partner_id,
                                            'phone':partner.mobile,
                                            'attachment_ids': False,
                                            'company_id': provider.company_id.id,
                                            'date':datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                            }
                                    if mes['quotedMsgId'] != None:
                                        request.env['whatsapp.history'].sudo().with_context(
                                            {'quotedMsgId': mes.get('quotedMsgId')}).create(vals)

                                    else:
                                        request.env['whatsapp.history'].sudo().create(vals)
                                elif mes['type'] == 'location':
                                    # phone change to mobile
                                    latlng = mes.get('body').split(";")
                                    vals = {
                                        'message': "<a href='https://www.google.com/maps/search/?api=1&query=" + str(
                                            latlng[0]) + "," + str(
                                            latlng[1]) + "' target='_blank' class='btn btn-primary'>Google Map</a>",
                                        'message_id': mes['id'],
                                        'author_id': user_partner.id,
                                        'type': 'received',
                                        'partner_id': partner_id,
                                        'phone': partner.mobile,
                                        'attachment_ids': False,
                                        'provider_id':provider.id,
                                        'company_id':provider.company_id.id,
                                        'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                    }
                                    if mes['quotedMsgId'] != None:
                                        request.env['whatsapp.history'].sudo().with_context(
                                            {'quotedMsgId': mes['quotedMsgId']}).create(vals)
                                    else:
                                        request.env['whatsapp.history'].sudo().create(vals)
                                else:
                                    datas = base64.b64encode(requests.get(mes.get('body')).content)
                                    file_name = mes.get('body').rsplit('/', 1)[1]
                                    attachment_value = {
                                        'name': file_name,
                                        'datas': datas,
                                    }
                                    attachment = request.env['ir.attachment'].sudo().create(attachment_value)
                                    if mes['quotedMsgId'] != None:
                                        # phone change to mobile
                                        request.env['whatsapp.history'].sudo().with_context(
                                            {'quotedMsgId': mes['quotedMsgId']}).create(
                                            {'message': "",
                                             'message_id': mes['id'],
                                             'author_id': user_partner.id,
                                             'type': 'received',
                                             'partner_id': partner_id,
                                             'phone': partner.mobile,
                                             'attachment_ids': [(4, attachment.id)],
                                             'provider_id':provider.id,
                                             'company_id': provider.company_id.id,
                                             'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                             })
                                    else:
                                        # request.env['wa.msgs'].sudo().create(vals)
                                        # phone change to mobile
                                        res = request.env['whatsapp.history'].sudo().create(
                                            {'message': "",
                                             'message_id': mes['id'],
                                             'author_id': user_partner.id,
                                             'type': 'received',
                                             'partner_id': partner_id,
                                             'phone': partner.mobile,
                                             'attachment_ids': [(4, attachment.id)],
                                             'provider_id':provider.id,
                                             'company_id': provider.company_id.id,
                                             'date': datetime.datetime.fromtimestamp(int(mes.get('time'))),
                                             })
                            else:
                                channel = self.get_channel([partner_id], provider)
                                if channel:
                                    message_values = {
                                        'body': mes.get('body'),
                                        'author_id': provider.user_id.partner_id.id,
                                        'email_from': user_partner.email or '',
                                        'model': 'mail.channel',
                                        'message_type': 'wa_msgs',
                                        'wa_message_id': mes.get('id'),
                                        'isWaMsgs': True,
                                        'subtype_id': request.env['ir.model.data'].sudo()._xmlid_to_res_id(
                                            'mail.mt_comment'),
                                        # 'channel_ids': [(4, channel.id)],
                                        'partner_ids': [(4, user_partner.id)],
                                        'res_id': channel.id,
                                        'reply_to': user_partner.email,
                                        'company_id': provider.company_id.id,
                                    }

                                    if mes['type'] == 'location':
                                        latlng = mes.get('body').split(";")
                                        message_values.update({
                                            'body': "<a href='https://www.google.com/maps/search/?api=1&query=" + str(
                                                latlng[0]) + "," + str(latlng[
                                                                           1]) + "' target='_blank' class='btn btn-primary'>Google Map</a>"})
                                    elif mes['type'] not in ['chat', 'location']:
                                        datas = base64.b64encode(requests.get(mes.get('body')).content)
                                        file_name = mes.get('body').rsplit('/', 1)[1]
                                        attachment_value = {
                                            'name': file_name,
                                            'datas': datas,
                                        }
                                        attachment = request.env['ir.attachment'].sudo().create(attachment_value)

                                        if attachment:
                                            message_values.update({'body': '', 'attachment_ids': [(4, attachment.id)]})
                                    if mes.get('quotedMsgId') != None:
                                        parent_message = request.env['mail.message'].sudo().search_read(
                                            [('wa_message_id', '=', mes['quotedMsgId'])],
                                            ['id', 'body', 'chatter_wa_model', 'chatter_wa_res_id',
                                             'chatter_wa_message_id'])
                                        if len(parent_message) > 0:
                                            message_values.update({'parent_id': parent_message[0]['id']})
                                            if parent_message[0].get('chatter_wa_model') and parent_message[0].get(
                                                    'chatter_wa_res_id') and parent_message[0].get(
                                                'chatter_wa_message_id'):
                                                chatter_wa_message_values = {
                                                    'body': mes.get('body'),
                                                    'author_id': provider.user_id.partner_id.id,
                                                    'email_from': user_partner.email or '',
                                                    'model': parent_message[0].get('chatter_wa_model'),
                                                    'message_type': 'comment',
                                                    'isWaMsgs': True,
                                                    'subtype_id': request.env['ir.model.data'].sudo()._xmlid_to_res_id(
                                                        'mail.mt_comment'),
                                                    # 'channel_ids': [(4, channel.id)],
                                                    'partner_ids': [(4, user_partner.id)],
                                                    'res_id': parent_message[0].get('chatter_wa_res_id'),
                                                    'reply_to': user_partner.email,
                                                    'parent_id': parent_message[0].get('chatter_wa_message_id'),
                                                }
                                                if message_values.get('attachment_ids'):
                                                    chatter_wa_message_values.update(
                                                        {'body': '',
                                                         'attachment_ids': message_values.get('attachment_ids')})
                                                chatter_wa_message = request.env['mail.message'].sudo().create(
                                                    chatter_wa_message_values)
                                                notifications = channel._channel_message_notifications(
                                                    chatter_wa_message)
                                                request.env['bus.bus'].sendmany(notifications)

                                    if mes.get('self') == 0:
                                        message = request.env['mail.message'].sudo().with_context(
                                            {'whatsapp_application': True}).create(
                                            message_values)
                                        notifications = channel._channel_message_notifications(message)
                                        request.env['bus.bus'].sendmany(notifications)
        return wa_dict