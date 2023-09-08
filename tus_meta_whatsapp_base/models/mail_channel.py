from odoo import _, api, fields, models, modules, tools

class Channel(models.Model):

    _inherit = 'mail.channel'

    whatsapp_channel = fields.Boolean(string="Whatsapp Channel")