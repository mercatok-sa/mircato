from odoo import fields, models, api, _


class BactToWorkWiz(models.TransientModel):
    _name = 'back.work.wiz'

    leave_to_date = fields.Date()
    back_date = fields.Date()
    holiday_type_id = fields.Many2one(comodel_name='hr.leave.type', string='Holiday Type',
                                      domain=['|', ('requires_allocation', '=', 'no'),
                                              ('has_valid_allocation', '=', True)])
    check_back_date = fields.Boolean(compute='get_back_date')
    related_leave_id = fields.Many2one(comodel_name='hr.leave')

    @api.depends('leave_to_date')
    def get_back_date(self):
        for rec in self:
            rec.check_back_date = False
            if rec.back_date:
                if rec.leave_to_date < rec.back_date:
                    rec.check_back_date = True

    def action_create_renew_leave(self):
        for item in self:
            if item.check_back_date and item.holiday_type_id:
                print(item.check_back_date)
                print(item.holiday_type_id)
                created_leave = self.env['hr.leave'].create({
                    'holiday_status_id': item.holiday_type_id.id,
                    'employee_id': item.related_leave_id.employee_id.id,
                    'request_date_from': item.leave_to_date,
                    'request_date_to': item.back_date,
                    'date_from': item.leave_to_date,
                    'date_to': item.back_date,
                    'holiday_type': item.related_leave_id.holiday_type,
                    'name': "Renewed from leave " + str(item.related_leave_id.holiday_status_id.name) +
                            " - " + str(item.related_leave_id.name)
                })
                created_leave.action_validate()
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Created Leave'),
                    'res_id': created_leave.id,
                    'res_model': 'hr.leave',
                    'view_id': self.env.ref('hr_holidays.hr_leave_view_form_manager').id,
                    'view_mode': 'form',
                    'domain': [('id', '=', created_leave.id)]
                }
            else:
                item.related_leave_id.action_refuse()
                item.related_leave_id.action_draft()
                item.related_leave_id.update({'request_date_to': item.back_date,'date_to': item.back_date})
                # item.related_leave_id.action_confirm()
                # item.related_leave_id.action_approve()
                # item.related_leave_id.action_validate()
