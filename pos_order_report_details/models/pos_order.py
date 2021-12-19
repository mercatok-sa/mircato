# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosOrderInherit(models.Model):
    _inherit = "pos.order"

    config_id = fields.Many2one('pos.config',
                                related='session_id.config_id',
                                string="Point of Sale",
                                readonly=False,
                                store=True)
    pos_date_order = fields.Date(compute="_compute_pos_date_order", store=True)

    @api.depends('date_order')
    def _compute_pos_date_order(self):
        for pos in self:
            if pos.date_order:
                pos.pos_date_order = pos.date_order.date()

    def _update_pos_date_order(self):
        all_pos_order_ids = self.env['pos.order'].search([])
        for pos in all_pos_order_ids:
            if pos.date_order:
                pos.pos_date_order = pos.date_order.date()
