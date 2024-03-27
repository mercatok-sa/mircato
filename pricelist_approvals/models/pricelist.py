from odoo import fields, models, api, _


class PriceList(models.Model):
    _inherit = 'product.pricelist'

    state = fields.Selection(selection=[('draft', 'Draft'), ('valid', 'Valid')], default='draft')

    def action_validate(self):
        for item in self:
            if self.env.user.has_group('pricelist_approvals.group_make_pricelist_valid'):
                item.update({'state': 'valid', 'validated': True})

    check_pricelist_validity = fields.Boolean(compute='check_price_list_validity',
                                              default=lambda self: self.env.user.has_group(
                                                  'pricelist_approvals.group_make_pricelist_valid'))

    def check_price_list_validity(self):
        for rec in self:
            rec.check_pricelist_validity = self.env.user.has_group('pricelist_approvals.group_make_pricelist_valid')

    validated = fields.Boolean()