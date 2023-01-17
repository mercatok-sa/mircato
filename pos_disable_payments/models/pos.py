# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_allow_numpad=fields.Boolean("Allow Numpad")
    is_allow_payments = fields.Boolean('Allow Payments')
    is_allow_discount = fields.Boolean('Allow Discount')
    is_allow_qty = fields.Boolean('Allow Qty')
    is_edit_price = fields.Boolean('Allow Edit Price')
    is_allow_remove_orderline = fields.Boolean('Allow Remove Order Line')
    is_allow_customer_selection=fields.Boolean("Allow Customer Selection")
    is_allow_plus_minus_button=fields.Boolean("Allow +/- Button")

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    is_allow_numpad=fields.Boolean("Allow Numpad")
    is_allow_payments = fields.Boolean('Allow Payments')
    is_allow_discount = fields.Boolean('Allow Discount')
    is_allow_qty = fields.Boolean('Allow Qty')
    is_edit_price = fields.Boolean('Allow Edit Price')
    is_allow_remove_orderline = fields.Boolean('Allow Remove Order Line')
    is_allow_customer_selection=fields.Boolean("Allow Customer Selection")
    is_allow_plus_minus_button=fields.Boolean("Allow +/- Button")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def open_employee_user(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window',
                'res_model': 'res.users',
                'view_mode': 'form',
                'res_id': self.user_id.id,
                'target': 'current',
                }
