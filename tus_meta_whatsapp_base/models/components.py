from odoo import api, fields, models, _


class Components(models.Model):
    _name = "components"
    _description = 'Whatsapp Components'

    type = fields.Selection([('header', 'HEADER'),
                            ('body', 'BODY'),
                            ('footer', 'FOOTER')],
                            'Type', default='header')
    formate = fields.Selection([('text', 'TEXT'),
                            ('media', 'MEDIA')],
                            'Formate', default='text')

    media_type = fields.Selection([('document', 'DOCUMENT'),
                            ('video', 'VIDEO'),
                            ('image', 'IMAGE'),],
                            'Media Type', default='document')

    text = fields.Text('Text')

    variables_ids = fields.One2many('variables','component_id','Variables')
    wa_template_id = fields.Many2one('wa.template')
    model_id = fields.Many2one('ir.model')

