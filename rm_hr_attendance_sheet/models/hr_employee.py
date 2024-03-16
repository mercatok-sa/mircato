from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    get_inf_from_planning = fields.Boolean(string="Planning Attendance Data", )


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    get_inf_from_planning = fields.Boolean(string="Planning Attendance Data", )
