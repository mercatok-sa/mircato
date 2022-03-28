# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
class AccountInvoice(models.Model):

    _inherit= "account.move"

    petty_id = fields.Many2many('petty.cash',string='Petty Cash')