# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class import_logs(models.TransientModel):
    _name = "import.logs"

    name = fields.Text(string='Logs')
