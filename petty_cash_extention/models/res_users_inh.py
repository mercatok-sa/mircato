# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
class Users(models.Model):
    _inherit = 'res.users'

    show_emps_petty_cashes = fields.Boolean('Show emps Petty Cashes')
