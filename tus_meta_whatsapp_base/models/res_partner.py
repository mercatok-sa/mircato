from odoo import _, api, fields, models, modules, tools
import requests
import json
from odoo.exceptions import UserError, ValidationError,AccessError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_whatsapp_number = fields.Boolean('Is Whatsapp Number')
    channel_provider_line_ids = fields.One2many('channel.provider.line', 'partner_id', 'Channel Provider Line')

    def check_whatsapp_number(self):
        # Multi Companies and Multi Providers Code Here
        # provider = self.env.user.provider_id
        # provider = self.env.user.provider_ids.filtered(lambda x: x.company_id == self.env.company)
        provider = False
        if self.env.user:
            provider = self.env.user.provider_ids.filtered(lambda x: x.company_id == self.env.company)
            if provider:
                provider = provider[0]
        if provider:
            # phone change to mobile
            if self.mobile:
                answer = provider.check_phone(self.mobile.strip('+').replace(" ", ""))
                if answer.status_code == 200:
                    dict = json.loads(answer.text)
                    if 'result' in dict:
                        if dict['result'] == 'exists':
                            self.is_whatsapp_number = True
                        else:
                            raise UserError(
                                ("please check your whatsapp number."))
        else:
            raise AccessError(_("Please add provider in User!"))

    @api.model
    def im_search(self, name, limit=20):
        """ Search partner with a name and return its id, name and im_status.
            Note : the user must be logged
            :param name : the partner name to search
            :param limit : the limit of result to return
        """
        # This method is supposed to be used only in the context of channel creation or
        # extension via an invite. As both of these actions require the 'create' access
        # right, we check this specific ACL.
        if self.env['mail.channel'].check_access_rights('create', raise_exception=False):
            name = '%' + name + '%'
            excluded_partner_ids = [self.env.user.partner_id.id]
            self.env.cr.execute("""
                            SELECT
                                P.id as id,
                                P.name as name
                            FROM res_partner P
                            WHERE P.name ILIKE %s
                                AND P.id NOT IN %s
                            LIMIT %s
                        """, (name, tuple(excluded_partner_ids), limit))
            return self.env.cr.dictfetchall()
        else:
            return {}

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        # phone change to mobile
        if res.mobile:
            res.mobile = res.mobile.strip('+').replace(" ", "")
        return res

    def write(self, vals):
        if 'mobile' in vals:
            if vals.get('mobile'):
                vals.update({'mobile':vals.get('mobile').strip('+').replace(" ", "")})
        res= super(ResPartner, self).write(vals)
        return res

