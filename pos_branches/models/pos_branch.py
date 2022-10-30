from odoo import api, fields, models, _


class POSBranch(models.Model):
    _name = 'pos.branch'
    _description = 'POS Branch'

    name = fields.Char(string=_('Branch Name'))
    pos_config_ids = fields.One2many('pos.config', 'branch_id')

    @api.model
    def crate(self, vals):
        result = super(POSBranch, self).crate(vals)

        return result
