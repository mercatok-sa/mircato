# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GeideaTerminals(models.Model):
    _name = 'geidea.terminals'

    name = fields.Char()
    ConnectionMode = fields.Selection([
        ('COM', 'Serial'),
        ('TCP', 'Network'),
    ], default='COM')
    ComName = fields.Char()
    BaudRate = fields.Char(default='38400')
    DataBits = fields.Char(default='8')
    Parity = fields.Char(default='none')
    IpAddress = fields.Char()
    Port = fields.Integer()
    PrintSettings = fields.Selection([
        ('1', 'Yes'),
        ('0', 'No')
    ], default='1')
    AppId = fields.Char(default='11')
