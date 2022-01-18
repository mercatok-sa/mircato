# -*- coding: utf-8 -*-
"""Classes defining the populate factory for Journal Entries, Invoices and related models."""
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class MircatoAccountMove(models.Model):

    _inherit = "account.move"

    @api.model
    def _get_default_journal(self):
        return super(MircatoAccountMove, self)._get_default_journal()

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 check_company=True,
                                 default=_get_default_journal)
