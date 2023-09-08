# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    PrimaryAccountNumber = fields.Char()
    RetrievalReferenceNumber = fields.Char()
    TransactionAuthCode = fields.Char()
