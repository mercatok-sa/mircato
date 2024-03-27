from odoo import api, fields, models



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name_ar = fields.Char('Arabic Name', compute='_calc_name_ar',readonly=True,required=False)

    @api.depends('name')
    def _calc_name_ar(self):

        env_ar = self.env(context=dict(self._context, lang='ar_001'))
        for record in self:
            data = env_ar[self._name].browse(record.id).read(['name'])
            print(data)
            if data:
                name_ar = data[0]['name']
                if record.name != name_ar:
                    record.name_ar = name_ar
                else:
                    record.name_ar=False

            else:
                
                record.name_ar = False

