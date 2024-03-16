# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo import models, fields, api, exceptions
from odoo import tools, _
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo.osv import expression


class Allowance(models.Model):
    _name = 'hr.allowance'
    _rec_name = 'name'
    _description = 'Allowance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Allowance Name", required=True)
    active = fields.Boolean(string="Active", default=True)


class ContractAllowanceLine(models.Model):
    _name = 'hr.contract.allowance.line'
    _rec_name = 'allowance_id'
    _description = 'Contract Allowance Line'

    allowance_id = fields.Many2one(comodel_name="hr.allowance", string="Allowance")
    contract_id = fields.Many2one(comodel_name="hr.contract", string="Contract")
    amount = fields.Float(string="Amount")


class Contract(models.Model):
    _name = "hr.contract"
    _inherit = 'hr.contract'

    annual_leave_per_day = fields.Float(string="Anuual Leave Per Day", required=True, default=30)
    amount = fields.Float(string="amount", compute='get_all_allowances_amount', store=True)
    rule_id = fields.Many2one('hr.config.rules', string="Indemnity Rule Name")
    time_off_policy_id = fields.Many2one('time.off.policy', string="Time Off Policy")

    @api.model
    def update_state(self):
        contracts_obj = self.env['hr.contract'].search([('date_end', '!=', False)])
        contracts = contracts_obj.search([
            ('state', '=', 'open'), ('kanban_state', '!=', 'blocked'),
            '|',
            '&',
            ('date_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=7))),
            ('date_end', '>=', fields.Date.to_string(date.today() + relativedelta(days=1))),
            '&',
            ('visa_expire', '<=', fields.Date.to_string(date.today() + relativedelta(days=60))),
            ('visa_expire', '>=', fields.Date.to_string(date.today() + relativedelta(days=1))),
        ])

        for contract in contracts:
            contract.activity_schedule(
                'mail.mail_activity_data_todo', contract.date_end,
                _("The contract of %s is about to expire.", contract.employee_id.name),
                user_id=contract.hr_responsible_id.id or self.env.uid)

        # contracts.write({'kanban_state': 'blocked'})

        self.search([
            ('state', '=', 'open'),
            '|',
            ('date_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=1))),
            ('visa_expire', '<=', fields.Date.to_string(date.today() + relativedelta(days=1))),
        ]).write({
            'state': 'close'
        })

        self.search([('state', '=', 'draft'), ('kanban_state', '=', 'done'),
                     ('date_start', '<=', fields.Date.to_string(date.today())), ]).write({
            'state': 'open'
        })

        # contract_ids = self.search([('date_end', '=', False), ('state', '=', 'close'), ('employee_id', '!=', False)])
        # Ensure all closed contract followed by a new contract have a end date.
        # If closed contract has no closed date, the work entries will be generated for an unlimited period.
        # for contract in contract_ids:
        #     next_contract = self.search([
        #         ('employee_id', '=', contract.employee_id.id),
        #         ('state', 'not in', ['cancel', 'new']),
        #         ('date_start', '>', contract.date_start)
        #     ], order="date_start asc", limit=1)
        #     if next_contract:
        #         contract.date_end = next_contract.date_start - relativedelta(days=1)
        #         continue
        #     next_contract = self.search([
        #         ('employee_id', '=', contract.employee_id.id),
        #         ('date_start', '>', contract.date_start)
        #     ], order="date_start asc", limit=1)
        #     if next_contract:
        #         contract.date_end = next_contract.date_start - relativedelta(days=1)

        return True

    @api.constrains('state')
    def _check_state(self):
        for record in self:
            if record.state == 'open':
                contract_ids = self.env['hr.contract'].search(
                    [('employee_id', '=', record.employee_id.id), ('state', '=', 'open')])
                if len(contract_ids) > 1:
                    raise exceptions.ValidationError(_('Employee Must Have Only One Running Contract'))

    allowances_ids = fields.One2many(comodel_name="hr.contract.allowance.line", inverse_name="contract_id")

    def get_all_allowances(self):
        return sum(self.allowances_ids.mapped('amount'))

    @api.depends('allowances_ids', 'allowances_ids.amount')
    def get_all_allowances_amount(self):
        for rec in self:
            rec.amount = sum(rec.allowances_ids.mapped('amount'))
