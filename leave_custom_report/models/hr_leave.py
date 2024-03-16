from odoo import fields, models, api, _


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    contract_id = fields.Many2one(comodel_name='hr.contract', compute='get_contract_id')

    @api.depends('employee_id')
    def get_contract_id(self):
        for item in self:
            item.contract_id = False
            if item.employee_id:
                contract = self.env['hr.contract'].search([('employee_id', '=', item.employee_id.id)], limit=1)
                if contract:
                    item.contract_id = contract.id

    last_return_leave_date = fields.Date(compute='get_last_date')

    @api.depends('employee_id')
    def get_last_date(self):
        for rec in self:
            rec.last_return_leave_date = False
            if rec.employee_id:
                last_leave = self.env['hr.leave'].search(
                    [('employee_id', '=', rec.employee_id.id), ('id', '!=', rec.id)],
                    order='create_date asc', limit=1)
                if last_leave:
                    rec.last_return_leave_date = last_leave.request_date_to

    address_in_leave = fields.Char()
