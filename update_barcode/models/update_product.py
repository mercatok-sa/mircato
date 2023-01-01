from odoo import api, fields, models, _

class POSConfig(models.Model):
    _inherit = 'product.product'

    barcode = fields.Char('Barcode', search='_search_barcode')
    
    def update_barcode(self):
        for ref in self.env['product.template'].search([]):
            print("Barcode::",ref.default_code,"\n\n")
            ref.barcode=ref.default_code
            
            
                
            
        
