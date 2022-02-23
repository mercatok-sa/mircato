# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class sale_configuration_settings(models.TransientModel):
    _inherit = "res.config.settings"

    commission_configuration = fields.Selection([('sale_order', 'Commission based on sales order'),
                                                 ('invoice', 'Commission based on invoice'),
                                                 ('payment', 'commission based on payment')
                                                 ], string='Generate Commision Entry Based On ',
                                                related="company_id.commission_configuration", readonly=False)

    commission_discount_account = fields.Many2one('account.account', domain=[('user_type_id', '=', 'Expenses')],
                                                  string="Commission Account",
                                                  related="company_id.commission_discount_account", readonly=False)


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    commission_configuration = fields.Selection([('sale_order', 'Commission based on sales order'),
                                                 ('invoice', 'Commission based on invoice'),
                                                 ('payment', 'commission based on payment')
                                                 ], string='Generate Commision Entry Based On ', default='payment')

    commission_discount_account = fields.Many2one('account.account', domain=[('user_type_id', '=', 'Expenses')],
                                                  string="Commission Account")
