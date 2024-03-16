# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, tools, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
import babel

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"


class AttendanceSheetBatch(models.Model):
    _name = 'attendance.sheet.batch'
    name = fields.Char("name")
    department_id = fields.Many2one('hr.department', 'Department Name', required=True)
    date_from = fields.Date(string='Date From', readonly=True, required=True,
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)), )
    date_to = fields.Date(string='Date To', readonly=True, required=True,
                          default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1,
                                                                                                     days=-1)).date()))
    att_sheet_ids = fields.One2many(comodel_name='attendance.sheet', string='Attendance Sheets',
                                    inverse_name='batch_id')
    payslip_batch_id = fields.Many2one(comodel_name='hr.payslip.run', string='Payslip Batch')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('att_gen', 'Attendance Sheets Generated'),
        ('att_sub', 'Attendance Sheets Submitted'),
        ('done', 'Close')], default='draft', track_visibility='onchange',
        string='Status', required=True, readonly=True, index=True, )

    @api.onchange('department_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if (not self.department_id) or (not self.date_from) or (
                not self.date_to):
            return
        department = self.department_id
        date_from = self.date_from
        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang', 'en_US')
        self.name = _('Attendance Batch of %s  Department for %s') % (
            department.name,
            tools.ustr(
                babel.dates.format_date(date=ttyme,
                                        format='MMMM-y',
                                        locale=locale)))

    def action_done(self):
        for batch in self:
            if batch.state != "att_sub":
                continue
            for sheet in batch.att_sheet_ids:
                if sheet.state == 'confirm':
                    sheet.action_approve()
            batch.write({'state': 'done'})

    def action_att_gen(self):
        return self.write({'state': 'att_gen'})

    def gen_att_sheet(self):

        att_sheets = self.env['attendance.sheet']
        att_sheet_obj = self.env['attendance.sheet']
        for batch in self:
            from_date = batch.date_from
            to_date = batch.date_to
            employee_ids = self.env['hr.employee'].search(
                [('department_id', '=', batch.department_id.id)])

            if not employee_ids:
                raise UserError(_("There is no  Employees In This Department"))
            for employee in employee_ids:

                contract_ids = employee._get_contracts(from_date, to_date)

                if not contract_ids:
                    raise UserError(_(
                        "There is no  Running contracts for :%s " % employee.name))
                new_sheet = att_sheet_obj.new({
                    'employee_id': employee.id,
                    'date_from': from_date,
                    'date_to': to_date,
                    'batch_id': batch.id
                })
                new_sheet.onchange_employee()
                values = att_sheet_obj._convert_to_write(new_sheet._cache)
                att_sheet_id = att_sheet_obj.create(values)

                att_sheet_id.get_attendances()
                att_sheets += att_sheet_id
            batch.action_att_gen()

    def submit_att_sheet(self):
        for batch in self:
            if batch.state != "att_gen":
                continue
            for sheet in batch.att_sheet_ids:
                if sheet.state == 'draft':
                    sheet.action_confirm()

            batch.write({'state': 'att_sub'})
