from odoo import api, fields, models, _


class Variables(models.Model):
    _name = "variables"
    _description = 'Whatsapp Variables'

    def _get_model_fields(self):
        domain = []
        if self._context and self._context.get('default_model_id'):
            domain =  [('model_id','=',self._context.get('default_model_id'))]
        return domain

    field_id = fields.Many2one('ir.model.fields','Field',domain=_get_model_fields)
    component_id = fields.Many2one('components')
    model_id = fields.Many2one('ir.model')
