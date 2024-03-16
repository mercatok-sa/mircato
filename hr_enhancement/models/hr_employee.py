from odoo import fields, models, api, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    delegation_required = fields.Boolean()
    passport_location = fields.Selection(selection=[('with_emp', 'مع الموظف'),
                                                    ('with_comp', 'مع الشركة')], tracking=True,
                                         string='Passport Location')
    probation_date_end = fields.Date('Probation Period End')

    identification_expiry_date = fields.Date()
    passport_expiry_date = fields.Date()
    medical_card_number = fields.Char()
    medical_card_expiry_date = fields.Date()
    bank_card_expiry_date = fields.Date()


class HrEmployeesPublic(models.Model):
    _inherit = 'hr.employee.public'

    delegation_required = fields.Boolean()
    passport_location = fields.Selection(selection=[('with_emp', 'مع الموظف'),
                                                    ('with_comp', 'مع الشركة')], tracking=True, string='مكان الجواز')
    probation_date_end = fields.Date('Probation Period End')

    identification_expiry_date = fields.Date()
    passport_expiry_date = fields.Date()
    medical_card_number = fields.Char()
    medical_card_expiry_date = fields.Date()
    bank_card_expiry_date = fields.Date()
