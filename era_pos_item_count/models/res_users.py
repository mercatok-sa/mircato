# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    display_all_info_close_session = fields.Boolean("Display all information Close Session")

