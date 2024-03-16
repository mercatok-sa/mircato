from odoo import fields, models, api, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    penalty_count = fields.Integer(compute='compute_count')

    def compute_count(self):
        for record in self:
            record.penalty_count = self.env['penalty.request'].search_count(
                [('employee_id', '=', record.id)])

    def get_penalties(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Penalties',
            'view_mode': 'tree,form',
            'res_model': 'penalty.request',
            'domain': [('employee_id', '=', self.id)],
        }
