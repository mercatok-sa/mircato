# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _get_pos_model_template(self):
        active_model = 'pos.order'
        domain = [('model', '=', active_model),('state','=','added')]

        # Multi Companies and Multi Providers Code Here
        #provider_id = self.env.user.provider_ids.filtered(lambda x: x.company_id == self.env.company)
        if self.env.user:
            provider_id = self.env.user.provider_ids.filtered(lambda x: x.company_id == self.env.company)
            if provider_id:
                provider_id = provider_id[0]

        # if self.env.user.provider_id:
        if provider_id:
            domain.append(('provider_id', '=', provider_id.id))
        else:
            domain.append(('create_uid', '=', self.env.user.id))
        return domain

    send_pos_receipt_on_validate = fields.Boolean(string="Send Pos Receipt On Validate")
    template_id = fields.Many2one(
        'wa.template', 'Use template', index=True, domain=_get_pos_model_template
    )
    provider_id = fields.Many2one('provider', 'Provider')
    allowed_provider_ids = fields.Many2many('provider', 'Provider', compute='update_allowed_providers')

    @api.depends('company_id')
    def update_allowed_providers(self):
        self.allowed_provider_ids = self.env.user.provider_ids

    @api.onchange('company_id', 'provider_id')
    def onchange_company_provider(self):
        self.template_id = False
        return {'domain': {'template_id': [('model_id.model', '=', 'pos.order'), ('provider_id', '=', self.provider_id.id)]}}