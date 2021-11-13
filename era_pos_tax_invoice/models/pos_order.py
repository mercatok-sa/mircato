
from odoo import models, fields, api

class POSConfigInherit(models.Model):
    _inherit = 'pos.config'

    allow_qr_code = fields.Boolean(string="Add QR Code in Receipt")

