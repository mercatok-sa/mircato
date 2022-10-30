from odoo import api, fields, models, _

class POSConfig(models.Model):
    _inherit = 'pos.config'

    branch_id = fields.Many2one('pos.branch')
