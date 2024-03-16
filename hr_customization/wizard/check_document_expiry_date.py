# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError
from calendar import monthrange
from datetime import date, datetime, time, timedelta
from datetime import datetime
import calendar


class CheckDocumentExpiryDate(models.TransientModel):
    _name = "check.document.expiry.date"

    def get_first_day_in_month(self):
        current_date = fields.Date().today()
        return current_date

    def get_last_day_in_month(self):
        current_date = fields.Date().today()
        e_date = current_date.replace(year=current_date.year, month=current_date.month + 1, day=current_date.day)
        return e_date

    date_from = fields.Date(string="Date From", default=get_first_day_in_month)
    date_to = fields.Date(string="Date To", default=get_last_day_in_month)

    def get_employee_document_expiry_date(self):
        documents = []
        employee_obj = self.env['hr.employee.document'].search([])
        for rec in employee_obj:
            if self.date_from <= rec.expiry_date < self.date_to:
                documents.append(rec.id)
        return {
            'name': _('Employee Document Expiry Date'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'hr.employee.document',
            'view_id': self.env.ref('hr_customization.check_employee_document_expiry_date_tree').id,
            'target': 'current',
            'domain': [('id', 'in', documents)]
        }
