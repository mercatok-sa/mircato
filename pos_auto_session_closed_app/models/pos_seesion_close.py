# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class PosSession(models.Model):
    _inherit = 'pos.session'

    track_ids = fields.One2many('log.track', 'session_id',  string='Log Track')
    
    @api.model
    def _pos_session_closed(self):
        records = self.env['pos.session'].search([
            ('state', '=', 'opened'),
            ])
        for session in records:
            session.action_pos_session_closing_control()
            if session.state == 'closed':
                self.env['log.track'].create({
                    'session_id': session.id,
                    'date': session.stop_at,
                    'error':'Successfull.....',
                })
            if session.cash_register_difference < 0.0:
                name = _('Loss')
            else:
                name= _('Profit')
            if session.state == 'closing_control':
                self.env['log.track'].create({
                    'session_id': session.id,
                    'date': session.stop_at,
                    'error':'There is no account defined on the journal %s for %s involved in a cash difference.'% (session.cash_journal_id.name,name),
                })    
  
class LogTrack(models.Model):
    _name = 'log.track'
    _rec_name = 'session_id'

    session_id = fields.Many2one('pos.session',  string='Session')
    date = fields.Datetime(string='Date', related='session_id.stop_at')
    error = fields.Text(string='Error')
