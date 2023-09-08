from odoo import models, api, fields , _
from odoo.http import request
import requests
import json
from odoo.exceptions import UserError
import time
import string
import secrets
from odoo.modules.module import get_module_resource
import base64
import io
from PIL import Image, ImageFile
import tempfile
import shutil
import os


class Provider(models.Model):
    _inherit = 'provider'

    provider = fields.Selection(
        selection_add=[('graph_api', "Graph API")], ondelete={'graph_api': 'set default'})
    graph_api_url = fields.Char(String="API URL")
    graph_api_instance_id = fields.Char(String="Instance ID")
    graph_api_business_id = fields.Char(String="WhatsApp Business Account ID")
    graph_api_token = fields.Char(String="Token")
    graph_api_authentication = fields.Selection(
        [('no_auth', 'No Auth'), ('basic_auth', "Basic Auth"), ('bearer_token', "Bearer Token")], default='no_auth',
        string='Authentication')
    graph_api_authenticated = fields.Boolean('Authenticated')
    user_id = fields.Many2one(string="User", comodel_name='res.users')

    is_token_generated = fields.Boolean('Is Token Generated')
    call_back_url = fields.Html(String="Call Back URL & Verify Token")


    def GenerateVerifyToken(self):
        seconds = time.time()
        unix_time_to_string = str(seconds).split('.')[0]  # time.time() generates a float example 1596941668.6601112
        alphaNumeric = string.ascii_uppercase + unix_time_to_string
        alphaNumericlower = string.ascii_lowercase + unix_time_to_string
        firstSet = ''.join(secrets.choice(alphaNumeric) for i in range(4))
        secondSet = ''.join(secrets.choice(alphaNumeric) for i in range(4))
        thirdSet = ''.join(secrets.choice(alphaNumericlower) for i in range(4))
        forthSet = ''.join(secrets.choice(alphaNumeric) for i in range(4))
        fifthset = ''.join(secrets.choice(alphaNumericlower) for i in range(4))
        token = firstSet + secondSet + thirdSet + forthSet + fifthset
        return token

    def reload_with_get_status(self):
        if self.graph_api_url and self.graph_api_instance_id and self.graph_api_token:
            url = self.graph_api_url + self.graph_api_instance_id + "?access_token=" + self.graph_api_token

            payload = {
                'full': True,
            }
            headers = {}
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if response.status_code == 200:
                dict = json.loads(response.text)
                if dict['id'] == self.graph_api_instance_id:
                    self.graph_api_authenticated = True

                    IrConfigParam = request.env['ir.config_parameter'].sudo()
                    base_url = IrConfigParam.get_param('web.base.url', False)

                    data = {
                        "webhookUrl": base_url + "/graph_tus/webhook"
                    }
                    verify_token = self.GenerateVerifyToken()
                    self.call_back_url = '<p>Now, You can set below details to your facebook configurations.</p><p>Call Back URL: <u><a href="%s">%s</a></u></p><p>Verify Token: <u style="color:#017e84">%s</u></p>' % (data.get('webhookUrl'), data.get('webhookUrl'),verify_token)
                    self.is_token_generated = True
            else:
                self.graph_api_authenticated = False
                self.call_back_url = '<p>Oops, something went wrong, Kindly Double Check the above Credentials. </p>'

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
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    # phone change to mobile
    def graph_api_direct_send_message(self, recipient, message):
        if self.graph_api_authenticated:
            data ={}
            # if quotedMsgId:
            #     data.update({'quotedMsgId':quotedMsgId})
                # phone change to mobile
            data = {
                "messaging_product": "whatsapp",
                "to": recipient.phone,
                "type": "text",
                "text": {
                    "body": message,
                }
            }
            url = self.graph_api_url + self.graph_api_instance_id + "/messages?access_token=" + self.graph_api_token
            headers = {
              'Content-Type': 'application/json',
              # 'Authorization': 'Bearer '+self.graph_api_token
            }
            try:
                answer = requests.post(url, data=json.dumps(data), headers=headers)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))
                
    def graph_api_send_message(self,recipient, message, quotedMsgId):
        if self.graph_api_authenticated:
            data ={}
            # if quotedMsgId:
            #     data.update({'quotedMsgId':quotedMsgId})
                # phone change to mobile
            data = {
                "messaging_product": "whatsapp",
                "to": recipient.mobile,
                "type": "text",
                "text": {
                    "body": message,
                }
            }
            url = self.graph_api_url + self.graph_api_instance_id + "/messages?access_token=" + self.graph_api_token
            headers = {
              'Content-Type': 'application/json',
              # 'Authorization': 'Bearer '+self.graph_api_token
            }
            try:
                answer = requests.post(url, data=json.dumps(data), headers=headers)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    # phone chnage to mobile
    def graph_api_direct_send_image(self, mobile, attachment_id):
        if self.graph_api_authenticated:
            datas = attachment_id.datas.decode("utf-8")
            data = {
                "phone": mobile,
                "body": "data:" + attachment_id.mimetype + ";base64," + datas,
                "filename": attachment_id.name,
            }
            url = self.graph_api_url + self.graph_api_instance_id + "/sendFile?access_token=" + self.graph_api_token
            headers = {'Content-type': 'application/json'}
            try:
                answer = requests.post(url, data=json.dumps(data), headers=headers)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    # phone change to mobile
    def graph_api_send_image(self, recipient, attachment_id):
        if self.graph_api_authenticated:
            file_name = attachment_id.name
            file_path = tempfile.gettempdir() + '/' + file_name
            temp_path = os.path.join(tempfile.gettempdir(), file_path)
            shutil.copy2(attachment_id._full_path(attachment_id.store_fname), temp_path)

            url = self.graph_api_url + self.graph_api_instance_id + "/media"

            payload = {'messaging_product': 'whatsapp'}
            files = [
                ('file', (attachment_id.name, open(file_path, 'rb'), attachment_id.mimetype))
            ]
            headers = {
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload, files=files)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def direct_get_image_by_id(self, media_id, recipient, sent_type, attachment_id):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/messages"
            data = {
                  "messaging_product": "whatsapp",
                  "recipient_type": "individual",
                  "to": recipient.phone,
                  "type": sent_type,
                  sent_type: {
                    "id": media_id
                  }
                }
            if sent_type == 'document':
                data[sent_type]['filename'] = attachment_id.name

            payload = json.dumps(data)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))
                
    def get_image_by_id(self, media_id, recipient, sent_type, attachment_id):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/messages"
            data = {
                  "messaging_product": "whatsapp",
                  "recipient_type": "individual",
                  "to": recipient.mobile,
                  "type": sent_type,
                  sent_type: {
                    "id": media_id
                  }
                }
            if sent_type == 'document':
                data[sent_type]['filename'] = attachment_id.name

            payload = json.dumps(data)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    # phone change to mobile
    def graph_api_check_phone(self, mobile):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/checkPhone?access_token=" + self.graph_api_token + "&phone=+" + mobile

            payload = {}
            headers = {}

            try:
                answer = requests.request("GET", url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))


    def send_image(self, recipient, attachment_id):
        t = type(self)
        fn = getattr(t, f'{self.provider}_send_image', None)
        res = fn(self, recipient, attachment_id)
        return res


    def graph_api_add_template(self, name, language, category, components):
        if self.graph_api_authenticated:
            data = {
                        "name": name,
                        "language": language,
                        "category": category,
                        "components": components,
                    }
            url = self.graph_api_url + self.graph_api_business_id + "/message_templates?access_token=" + self.graph_api_token

            headers = {'Content-type': 'application/json'}

            try:
                answer = requests.post(url, data=json.dumps(data), headers=headers)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def graph_api_direct_send_template(self, template, language, namespace, partner, params):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/messages"
            payload = json.dumps({
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": partner.phone,
                "type": "template",
                "template": {
                    "name": template,
                    "language": {
                        "code": language
                    },
                    "components": params
                }
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))
                
    def graph_api_send_template(self, template, language, namespace, partner, params):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/messages"
            payload = json.dumps({
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": partner.mobile,
                "type": "template",
                "template": {
                    "name": template,
                    "language": {
                        "code": language
                    },
                    "components": params
                }
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def graph_api_remove_template(self, name):
        if self.graph_api_authenticated:
            data = {
                        "name": name,
                        # "language": language,
                        # "category": category,
                        # "components": components,
                    }
            url = self.graph_api_url + self.graph_api_business_id + "/message_templates?name=" + name + "&access_token=" + self.graph_api_token
            headers = {'Content-type': 'application/json'}

            try:
                answer = requests.delete(url, data=json.dumps(data), headers=headers)
                # answer = requests.post(url, headers=headers, data=data)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
                        answer.text).get('error'):
                    dict = json.loads(answer.text).get('error').get('message')
                    raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def graph_api_wamsg_mark_as_read(self, message_id):
        """
        When Incoming WhatsApp Message Seen/Read in odoo, Double Blue Tick (Read Receipts) in WhatsApp
        """
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/messages"
            data = {
                  "messaging_product": "whatsapp",
                  "status": "read",
                  "message_id": message_id,
                }
            payload = json.dumps(data)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            # if answer.status_code != 200:
            #     if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
            #             answer.text).get('error'):
            #         dict = json.loads(answer.text).get('error').get('message')
            #         raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))                

