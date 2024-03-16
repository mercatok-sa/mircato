from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    change_price = fields.Boolean(compute='check_change_price',
                                  default=lambda self: self.env.user.has_group(
                                      'po_access_right.group_control_price_unit'))
    change_qty = fields.Boolean(compute='check_change_qty',
                                default=lambda self: self.env.user.has_group(
                                    'po_access_right.group_control_quantity'))
    change_taxes = fields.Boolean(compute='check_change_taxes',
                                  default=lambda self: self.env.user.has_group(
                                      'po_access_right.group_control_taxes'))

    def check_change_price(self):
        for rec in self:
            rec.change_price = self.env.user.has_group('po_access_right.group_control_price_unit')

    def check_change_qty(self):
        for rec in self:
            rec.change_qty = self.env.user.has_group('po_access_right.group_control_quantity')

    def check_change_taxes(self):
        for rec in self:
            rec.change_taxes = self.env.user.has_group('po_access_right.group_control_taxes')
