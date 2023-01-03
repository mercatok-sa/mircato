# -*- coding: utf-8 -*-
#################################################################################
# Author      : Zero For Information Systems (<www.erpzero.com>)
# Copyright(c): 2016-Zero For Information Systems
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError

class Company(models.Model):
    _inherit = 'res.company'

    activat_internal_trans = fields.Boolean(string="Activate accounts when transfer between different storage locations",)
    inter_locations_clearing_account_id = fields.Many2one('account.account',
        domain=lambda self: [('reconcile', '=', True), ('user_type_id.id', '=', self.env.ref('account.data_account_type_current_assets').id), ('deprecated', '=', False)], string="Inter-locations Clearing Account", help="Intermediary account used when moving stock from a storage Location to another different storage Location")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    activat_internal_trans = fields.Boolean(string="Activate accounts when transfer between different storage locations",related='company_id.activat_internal_trans', readonly=False)
    inter_locations_clearing_account_id = fields.Many2one('account.account', string="Inter-locations Clearing Account",
        related='company_id.inter_locations_clearing_account_id', readonly=False,
        domain=lambda self: [('reconcile', '=', True), ('user_type_id.id', '=', self.env.ref('account.data_account_type_current_assets').id)],
        help="Intermediary account used when moving stock from a storage Location to another different storage Location")
