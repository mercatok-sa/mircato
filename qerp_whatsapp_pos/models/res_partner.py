# -*- coding: utf-8 -*-

from odoo import api, models


class Partner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [
        ('unique_mobile', 'UNIQUE(mobile)', 'No duplication of Customer Mobile numbers')
    ]