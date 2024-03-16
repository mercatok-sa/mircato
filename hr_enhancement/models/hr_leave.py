from odoo import fields, models, api, _


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    delegation_id = fields.Many2one(comodel_name='hr.employee', string='Delegation')
    required_delegation = fields.Boolean(related='employee_id.delegation_required')

    def action_approve(self):
        for item in self:
            if item.delegation_id and item.delegation_id.work_email:
                template_id = self.env['ir.model.data']._xmlid_to_res_id('hr_enhancement.leave_delegation_send_mail',
                                                                         raise_if_not_found=False)
                template_id = self.env['mail.template'].browse(template_id)
                template_id.send_mail(item.id, True)
        return super(HrLeave, self).action_approve()

    def back_to_work(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Back To Work'),
            'res_model': 'back.work.wiz',
            'view_mode': 'form',
            'context': {'default_leave_to_date': self.request_date_to,
                        'default_related_leave_id': self.id},
            'target': 'new',
        }
