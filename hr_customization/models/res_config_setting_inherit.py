# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    indemnity_liability_account_id = fields.Many2one('account.account', string="Indemnity Liability Account")
    indemnity_expense_account_id = fields.Many2one('account.account', string="Indemnity Expense Account")
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal")

    def set_values(self):
        set_param = self.env['ir.config_parameter'].set_param
        set_param('indemnity_liability_account_id', (self.indemnity_liability_account_id.id))
        set_param('indemnity_expense_account_id', (self.indemnity_expense_account_id.id))
        set_param('journal_id', (self.journal_id.id))
        super(ResConfigSettings, self).set_values()

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            indemnity_liability_account_id=int(get_param('indemnity_liability_account_id')),
            indemnity_expense_account_id=int(get_param('indemnity_expense_account_id')),
            journal_id=int(get_param('journal_id'))
        )
        return res
