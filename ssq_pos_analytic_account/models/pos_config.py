from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Account")
