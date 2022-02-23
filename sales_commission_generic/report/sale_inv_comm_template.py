# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models


class sale_inv_comm_template(models.AbstractModel):
    _name = 'report.sales_commission_generic.sale_inv_comm_template'
    _description = 'Report sale inv comm template'

    def _get_report_values(self, docids, data=None):
        record_ids = self.env[data['model']].browse(data['form'])
        return {
            'doc_ids': self.ids,
            'doc_model': data['model'],
            'docs': self,
            'data': data,
            'ids': record_ids
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
