# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"


    group_refund_id = fields.Many2one("res.groups", compute="_compute_groups", 
        string="Point of Sale - Refund")

    def _compute_groups(self):
        self.group_refund_id = self.env.ref("era_pos_refund.group_refund").id,

