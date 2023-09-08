from odoo import _, api, fields, models, modules, tools
from itertools import chain
from odoo.exceptions import ValidationError
concat = chain.from_iterable

class ResUsers(models.Model):
    _inherit = 'res.users'

    provider_id = fields.Many2one('provider', 'Provider', domain="[('company_id', 'in', company_ids)]")
    provider_ids = fields.Many2many('provider', 'provider_rel', 'provider_id', 'pid', domain="[('company_id', 'in', company_ids)]", string='Providers')

    @api.constrains('provider_id', 'provider_ids', 'company_ids', 'company_id')
    def _check_company_providers(self):
        all_provider_by_company = self.env['provider'].sudo().search([('company_id', 'in', self.company_ids.ids)])

        provider_not_allowed = []
        for i in self.provider_ids:
            if i not in all_provider_by_company:
                provider_not_allowed.append(i.name)

        if provider_not_allowed and any(provider_not_allowed):
            raise ValidationError(
                _('For field Allowed Providers %(provider_name)s is not in the allowed providers for user %(user_name)s (%(provider_allowed)s).',
                  provider_name= ', '.join(provider_not_allowed),
                  user_name=self.name,
                  provider_allowed=', '.join(all_provider_by_company.mapped('name')))
            )
        if self.provider_id.id not in all_provider_by_company.ids:
            raise ValidationError(
            _('For field Default Provider %(provider_name)s is not in the allowed providers for user %(user_name)s (%(provider_allowed)s).',
              provider_name=self.provider_id.name,
              user_name=self.name,
              provider_allowed=', '.join(all_provider_by_company.mapped('name')))
            )

    '''
      Inherited Method
    '''
    def write(self, values):
        """
        Uncheck groups
        :param values: {}
        :return: {}
        """
        values = self._remove_reified_groups(values)
        if values.get('groups_id'):
            groups = values.get('groups_id')
            uncheck_ids = []
            whatsapp_manager_group = self.env.ref('tus_meta_whatsapp_base.whatsapp_group_manager').id
            inherited_groups = self.env['res.groups'].search(
                [('implied_ids', 'in', self.env.ref('tus_meta_whatsapp_base.whatsapp_group_user').ids)])
            for group in groups:
                if group[0] == 3 and group[1] == whatsapp_manager_group:
                    # implied_ids = self.env['res.groups'].sudo().browse(group[1]).implied_ids
                    gs = set(concat(g for g in inherited_groups))
                    uncheck_ids.extend([(3, g.id) for g in gs])
                if group[0] == 4 and group[1] == whatsapp_manager_group:
                    gs = set(concat(g for g in inherited_groups))
                    uncheck_ids.extend([(4, g.id) for g in gs])
            if uncheck_ids:
                values.get('groups_id').extend(uncheck_ids)
        return super(ResUsers, self).write(values)