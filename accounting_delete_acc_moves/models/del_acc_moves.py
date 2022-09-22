from odoo import models, fields, api, _
from datetime import timedelta, datetime, date

class _del_acc_move(models.Model):
    _inherit ='account.move'
    
    def del_acc_move(self):
        # self.env.cr.execute("delete from account_move where id in (select id from account_move limit 2)")
        

        for rec in self.env['account.move'].search([('state','!=','posted')], limit =1000):
            rec.unlink()
            
            # _logger.warning("Record deleted :" + str(rec.id)) 