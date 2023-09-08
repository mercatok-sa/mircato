from odoo import api, fields, models, _
import requests
import json
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
import base64

class WATemplate(models.Model):
    _name = "wa.template"
    _inherit = ['mail.render.mixin']
    _description = 'Whatsapp Templates'


    def init(self):
        video_path = get_module_resource('tus_meta_whatsapp_base', 'static/src/video', 'wa-demo-video.mp4')
        attachment = self.env['ir.attachment'].sudo().search([('name', '=', 'demo-wa-video')])
        if not attachment:
            attachment_value = {
                'name': 'demo-wa-video',
                'datas': base64.b64encode(open(video_path, 'rb').read()),
                'mimetype': 'video/mp4',
            }
            attachment = self.env['ir.attachment'].sudo().create(attachment_value)

        pdf_path = get_module_resource('tus_meta_whatsapp_base', 'static/src/pdf', 'TestPDFfile.pdf')
        attachment = self.env['ir.attachment'].sudo().search([('name', '=', 'demo-wa-pdf')])
        if not attachment:
            attachment_value = {
                'name': 'demo-wa-pdf',
                'datas': base64.b64encode(open(pdf_path, 'rb').read()),
                'mimetype': 'application/pdf',
            }
            attachment = self.env['ir.attachment'].sudo().create(attachment_value)

        pdf_path = get_module_resource('tus_meta_whatsapp_base', 'static/src/image', 'whatsapp_default_set.png')
        attachment = self.env['ir.attachment'].sudo().search([('name', '=', 'demo-wa-image')])
        if not attachment:
            attachment_value = {
                'name': 'demo-wa-image',
                'datas': base64.b64encode(open(pdf_path, 'rb').read()),
                'mimetype': 'image/png',
            }
            attachment = self.env['ir.attachment'].sudo().create(attachment_value)

    @api.model
    def default_get(self, fields):
        res = super(WATemplate, self).default_get(fields)
        if not fields or 'model_id' in fields and not res.get('model_id') and res.get('model'):
            res['model_id'] = self.env['ir.model']._get(res['model']).id
        return res

    def _get_current_user_provider(self):
        # Multi Companies and Multi Providers Code Here
        provider_id = self.env.user.provider_ids.filtered(lambda x: x.company_id == self.env.company)
        if provider_id:
            return provider_id[0]
        return False

    name = fields.Char('Name', translate=True, required=True)
    provider_id = fields.Many2one('provider', 'Provider', default=_get_current_user_provider) # default=lambda self: self.env.user.provider_id
    model_id = fields.Many2one(
        'ir.model', string='Applies to',
        help="The type of document this template can be used with", ondelete='cascade',)
    model = fields.Char('Related Document Model', related='model_id.model', index=True, store=True, readonly=True)
    body_html = fields.Html('Body', render_engine='qweb', translate=True, sanitize=False)
    state = fields.Selection([
        ('draft','DRAFT'),
        ('imported', 'IMPORTED'),
        ('added', 'ADDED TEMPLATE'),
        ], string='State', default='draft')
    namespace = fields.Char('Namespace')
    category = fields.Selection([('auto_reply', 'AUTO_REPLY'),
                                 ('account_update', 'ACCOUNT_UPDATE'),
                                 ('payment_update', 'PAYMENT_UPDATE'),
                                 ('personal_finance_update', 'PERSONAL_FINANCE_UPDATE'),
                                 ('shipping_update', 'SHIPPING_UPDATE'),
                                 ('reservation_update', 'RESERVATION_UPDATE'),
                                 ('issue_update', 'ISSUE_RESOLUTION'),
                                 ('appointment_update', 'APPOINTMENT_UPDATE'),
                                 ('transportation_update', 'TRANSPORTATION_UPDATE'),
                                 ('ticket_update', 'TICKET_UPDATE'),
                                 ('alert_update', 'ALERT_UPDATE'),
                                 ('transactional', 'TRANSACTIONAL'),
                                 ('marketing', 'MARKETING'),
                                 ('utility', 'UTILITY'),
                                 ('authentication', 'AUTHENTICATION')],
                                'Category', default='utility', required=True)
    # language = fields.Char("Language", default="en")
    lang = fields.Many2one("res.lang", "Language",required=True)
    components_ids = fields.One2many('components', 'wa_template_id', 'Components')
    graph_message_template_id = fields.Char(String="WhatsApp Graph Message Template ID")
    show_graph_message_template_id = fields.Boolean(compute='_compute_show_graph_message_template_id')

    @api.depends('provider_id')
    def _compute_show_graph_message_template_id(self):
        for message in self:
            if self.provider_id.provider == 'graph_api':
                message.show_graph_message_template_id = True
            else:
                message.show_graph_message_template_id = False
    # def init(self):
    #     video_path = get_module_resource('tus_meta_whatsapp_base', 'static/src/video', 'whatsapp_in_chatter.mp4')
    #     attachment = self.env['ir.attachment'].sudo().search([('name', '=', 'demo_wa_video')])
    #     if not attachment:
    #         attachment_value = {
    #             'name': 'demo_wa_video',
    #             'datas': base64.b64encode(open(video_path, 'rb').read()),
    #             'mimetype': 'video/mp4',
    #         }
    #         self.env['ir.attachment'].sudo().create(attachment_value)
    #
    #     pdf_path = get_module_resource('tus_meta_whatsapp_base', 'static/src/pdf', 'TestPDFfile.pdf')
    #     attachment = self.env['ir.attachment'].sudo().search([('name', '=', 'demo_wa_pdf')])
    #     if not attachment:
    #         attachment_value = {
    #             'name': 'demo_wa_pdf',
    #             'datas': base64.b64encode(open(pdf_path, 'rb').read()),
    #             'mimetype': 'application/pdf',
    #         }
    #         self.env['ir.attachment'].sudo().create(attachment_value)
    #
    #     pdf_path = get_module_resource('tus_meta_whatsapp_base', 'static/src/image', 'whatsapp_default_set.png')
    #     attachment = self.env['ir.attachment'].sudo().search([('name', '=', 'demo_wa_image')])
    #     if not attachment:
    #         attachment_value = {
    #             'name': 'demo_wa_image',
    #             'datas': base64.b64encode(open(pdf_path, 'rb').read()),
    #             'mimetype': 'image/png',
    #         }
    #         self.env['ir.attachment'].sudo().create(attachment_value)

    @api.depends('model')
    def _compute_render_model(self):
        for template in self:
            template.render_model = template.model

    @api.model
    def create(self, vals):
        res = super(WATemplate, self).create(vals)
        res.name = res.name.lower()
        return res

    def add_whatsapp_template(self):
        components = []
        for component in self.components_ids:
            dict = {}
            if component.type == 'header':
                if component.formate == 'media':
                    IrConfigParam = self.env['ir.config_parameter'].sudo()
                    base_url = IrConfigParam.get_param('web.base.url', False)

                    if component.media_type == 'document':
                        attachment = self.env['ir.attachment'].sudo().search([('name', '=', 'demo-wa-pdf')])
                        if attachment:
                            dict.update({"example": {
                                "header_handle": [
                                    base_url+"/web/content/"+str(attachment.id)
                                ]
                            }, 'type': component.type.upper(), 'format': component.media_type.upper(), })
                        components.append(dict)

                    if component.media_type == 'video':
                        attachment = self.env['ir.attachment'].sudo().search([('name','=','demo-wa-video')])
                        if attachment:
                            dict.update({"example": {
                                "header_handle": [
                                    base_url+"/web/content/"+str(attachment.id)
                                ]
                            }, 'type': component.type.upper(), 'format': component.media_type.upper(), })
                        components.append(dict)

                    if component.media_type == 'image':
                        attachment = self.env['ir.attachment'].sudo().search([('name', '=', 'demo-wa-image')])
                        if attachment:
                            dict.update({"example": {
                                    "header_handle": [
                                        base_url+"/web/image/ir.attachment/" + str(attachment.id)+"/datas"
                                    ]
                                },'type': component.type.upper(),'format':component.media_type.upper(),  })
                        components.append(dict)

                else:
                    body_text = []
                    for variable in component.variables_ids:
                        body_text.append('Test')
                    if body_text:
                        dict.update({"example": {
                            "body_text": [body_text
                                          ]}})
                    if component.text:
                        dict.update({'text': component.text, 'type': component.type.upper(),'format':component.formate.upper() })
                        components.append(dict)

            else:
                body_text = []
                for variable in component.variables_ids:
                    body_text.append('Test')
                if body_text:
                    dict.update({"example": {
                        "body_text": [body_text
                        ]}})
                if component.text:
                    dict.update({'text': component.text, 'type': component.type.upper(),})
                    components.append(dict)

        if components:

            answer = self.provider_id.add_template(self.name, self.lang.iso_code, self.category.upper(), components)
            if answer.status_code == 200:
                dict = json.loads(answer.text)

                if self.provider_id.provider == 'chat_api':
                    if 'message' in dict:
                        raise UserError(
                            (dict.get('message')))
                    if 'error' in dict:
                        raise UserError(
                            (dict.get('error').get('message')))
                    else:
                        if 'status' in dict and dict.get('status') == 'submitted':
                            self.state = 'added'
                            self.namespace = dict.get('namespace')

                if self.provider_id.provider == 'graph_api':
                    if 'message' in dict:
                        raise UserError(
                         (dict.get('message')))
                    if 'error' in dict:
                        raise UserError(
                         (dict.get('error').get('message')))
                    else:
                        if 'id' in dict:
                             self.state = 'added'
                             self.graph_message_template_id = dict.get('id')
        else:
            raise UserError(
                ("please add components!"))


    def remove_whatsapp_template(self):
        answer = self.provider_id.remove_template(self.name)
        if answer.status_code == 200:
            dict = json.loads(answer.text)
            if 'message' in dict:
                raise UserError(
                    (dict.get('message')))
            if 'error' in dict:
                raise UserError(
                    (dict.get('error').get('message')))
            if 'result' in dict and dict.get('result') == 'success':
                self.state = 'draft'
            if 'success' in dict and dict.get('success') == True:
                self.state = 'draft'
    def get_whatsapp_temaplate(self):
        for provider in self.env['provider'].search([]):
            if provider.chat_api_authenticated:
                response = provider.get_whatsapp_template()
                if response.status_code == 200:
                    dict = json.loads(response.text)
                    for template in dict.get('templates'):
                        if not self.search([('name', '=', template.get('name'))]):
                            if template.get('status') in ['approved','submitted']:
                                template_state = 'imported'
                                component_vals_list = []
                                for comp in template.get('components'):
                                    component_type = comp.get('type')
                                    # component_text = comp.get('text')
                                    comp_media_type = comp.get('format')
                                    # comp_formate_type = comp.get('formate')

                                    if component_type == 'HEADER':
                                        if comp_media_type == 'VIDEO' or 'DOCUMENT' or 'IMAGE' or 'TEXT':
                                            if comp_media_type == 'TEXT':
                                                compoment_ids = self.env['components'].create(
                                                    {'type': comp.get('type').lower(), 'formate': 'TEXT'.lower(),
                                                     'text': comp.get('text')})
                                                component_vals_list.append((4, compoment_ids.id))
                                            else:
                                                compoment_ids = self.env['components'].create(
                                                    {'type': comp.get('type').lower(), 'formate': 'MEDIA'.lower(),
                                                     'media_type': comp.get('format').lower()})
                                                component_vals_list.append((4, compoment_ids.id))
                                    else:
                                        compoment_ids = self.env['components'].create(
                                            {'type': comp.get('type').lower(), 'text': comp.get('text')})
                                        component_vals_list.append((4, compoment_ids.id))

                                vals = {
                                    'name': template.get('name'),
                                    'category': template.get('category').lower(),
                                    'provider_id': provider.id,
                                    'lang': self.env.ref('base.lang_en').id,
                                    'namespace': template.get('namespace'),
                                    'components_ids': component_vals_list,
                                    'state': template_state
                                }
                                self.create(vals)

    def add_imported_whatsapp_template(self):
        self.write({'state':'added'})


                


