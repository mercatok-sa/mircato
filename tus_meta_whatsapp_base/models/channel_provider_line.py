from odoo import _, api, fields, models, modules, tools

class ChannelProviderLine(models.Model):
    _description = 'Channel Provider Line'
    _name = 'channel.provider.line'

    channel_id = fields.Many2one('mail.channel','Channel')
    provider_id = fields.Many2one('provider', 'Provider')
    partner_id = fields.Many2one('res.partner','Partner')