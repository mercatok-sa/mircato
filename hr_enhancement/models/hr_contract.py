from odoo import fields, models, api, tools, _
from datetime import timedelta, datetime


class Contract(models.Model):
    _inherit = 'hr.contract'

    salary_in_work = fields.Monetary(string='الراتب في اذن العمل')
    probation_period = fields.Many2one(comodel_name='contract.probation.period', string='Probation Period',
                                       required=True)
    probation_date_end = fields.Date('Probation Period End', compute='get_probation_date_end')

    def get_probation_date_end(self):
        for rec in self:
            rec.probation_date_end = False
            if rec.probation_period:
                date_start = datetime.strptime(str(rec.date_start), '%Y-%m-%d')
                probation_end = rec.date_start + timedelta(days=int(rec.probation_period.name))
                end_date = datetime.strptime(str(probation_end), '%Y-%m-%d')

                work_data = rec.resource_calendar_id.get_work_duration_data(date_start, end_date)
                not_working_days = int(rec.probation_period.name) - work_data['days']

                public_holiday_days = self.env['hr.public.holiday'].search_count([
                    ('date_from', '>=', date_start), ('date_to', '<=', end_date), ('state', '=', 'active'),
                    '|', '|', ('emp_ids', 'in', rec.employee_id.id),
                    ('dep_ids', '=', rec.employee_id.department_id.id),
                    ('cat_ids', '=', rec.employee_id.category_ids.ids)
                ])

                resource_public_days = self.env['resource.calendar.leaves'].search_count([
                    ('date_from', '>=', date_start), ('date_to', '<=', end_date)])

                total_days = not_working_days + resource_public_days + public_holiday_days
                rec.probation_date_end = end_date + + timedelta(days=int(total_days))
                rec.employee_id.probation_date_end = rec.probation_date_end

    @api.model
    def mail_reminder(self):
        users = []
        for user in self.env['res.users'].search([]):
            if user.has_group('hr.group_hr_manager'):
                users.append(user.partner_id.id)
        for item in self:
            if item.probation_date_end:
                exp_date = item.probation_date_end - timedelta(days=7)
                if fields.Date().today() == exp_date:
                    mail_content = "  Hello  " + item.employee_id.name + ",<br>Your Probation Period " + item.name + \
                                   " is going to expire on " + str(item.probation_date_end) + "."
                    if len(users) > 0:
                        users = set(users)
                    post_vars = {
                        'subject': _('Document-%s Expired On %s') % (item.name, item.probation_date_end),
                        'title': 'Probation Period Expiration',
                        'body': mail_content, 'partner_ids': [(6, 0, users)]
                    }

                    self.env['mail.thread'].message_post(type="notification", subtype="mt_comment", **post_vars)
