from odoo import api, fields, models, _

class POSConfig(models.Model):
    _inherit = 'product.template'

    barcode = fields.char('')
    def _aupdate_barcode(self):
        for ref in self:
            ref.barcode=ref.default_code
            
                
            
        