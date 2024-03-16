# -*- coding: utf-8 -*-


from odoo import fields, models, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    promotion_ids = fields.One2many('hr.promotion', 'employee_id')
