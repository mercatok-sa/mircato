# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    is_affiliated = fields.Boolean(string="Affiliated", default=False,
                                   help="Check this box if this customer is Affiliated.")
