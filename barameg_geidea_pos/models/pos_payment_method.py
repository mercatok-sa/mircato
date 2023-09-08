# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GeideaPos(models.Model):
    _inherit = 'pos.payment.method'

    EnableGeidea = fields.Boolean()
    GeideaPort = fields.Char(default='5000')
    GeideaTerminal = fields.Many2one('geidea.terminals')
