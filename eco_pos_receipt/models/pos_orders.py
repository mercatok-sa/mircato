from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    global_total_discount = fields.Float(compute='get_global_total_discount')
    total_item_discount = fields.Float(compute='get_total_item_discount')
    refunded_order_number = fields.Char(string="", required=False, )

    @api.depends('lines.price_subtotal_incl')
    def get_global_total_discount(self):
        for item in self:
            item.global_total_discount = 0.0
            for line in item.mapped('lines'):
                if 'Discount' in line.full_product_name:
                    item.global_total_discount += round(abs(line.price_subtotal_incl), 3)

    @api.depends('lines.discount')
    def get_total_item_discount(self):
        for rec in self:
            rec.total_item_discount = 0.0
            for line in rec.mapped('lines'):
                if line.discount:
                    rec.total_item_discount += line.discount
