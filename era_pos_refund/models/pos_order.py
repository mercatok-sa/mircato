# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.osv.expression import AND


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def search_paid_order_ids(self, config_id, domain, limit, offset):
        """ Search for 'paid' orders for all pos """
        
        res = super(PosOrder, self).search_paid_order_ids(config_id, domain, limit, offset)
        default_domain = ['!', '|', ('state', '=', 'draft'), ('state', '=', 'cancelled')]
        ids = self.search(AND([domain, default_domain]), limit=limit, offset=offset).ids
        res['ids'] = ids
        return res
