# -*- coding: utf-8 -*-
import base64

from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo import http, fields, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.mimetypes import guess_mimetype

File_Type = ['application/pdf', 'image/jpeg', 'image/png']  # allowed file type


class CustomPortalTemplateRender(CustomerPortal):
    MANDATORY_BILLING_FIELDS = []
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "image_1920", "name", "email",
                               "phone", "city", "country_id"]

    _items_per_page = 20

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        employee = request.env['hr.employee'].sudo().search(
            ['|', ('address_id', '=', partner.id), ('user_id', '=', request.env.user.id)])

        if post and request.httprequest.method == 'POST':
            values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
            values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
            employee.sudo().write(values)
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        departments = request.env['hr.department'].sudo().search([])
        managers = request.env['hr.employee'].sudo().search([])
        job_titles = request.env['hr.job'].sudo().search([])

        values.update({
            'partner': employee,
            'countries': countries,
            'departments': departments,
            'managers': managers,
            'job_titles': job_titles,
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    #
    # @http.route(['/change/profile/'], type='http', auth="user", method="post", csrf=False, website=True)
    # def change_account_pic(self, **post):
    #     partner_id = request.env.user.partner_id
    #     if post.get('attachment', False):
    #         file = post.get('attachment')
    #         attachment = file.read()
    #         mimetype = guess_mimetype(base64.b64decode(base64.encodebytes(attachment)))
    #         if mimetype in File_Type:
    #             partner_id.sudo().write({'image_1920': base64.encodebytes(attachment)})
    #
    #     return request.redirect('/my/account')


class PromotionPortal(CustomerPortal):

    @http.route(['/my/promotions', '/my/promotions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_promotions(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        employee = request.env['hr.employee'].sudo().search([('user_id.partner_id', '=', partner.id)])
        promotions = request.env['hr.promotion'].sudo().search([('employee_id', '=', employee.id)])

        values.update({
            'page_name': 'Promotions',
            'promotions': promotions
        })
        return request.render("custom_portal_account_page.portal_my_promotion", values)


class HrPayroll(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'payroll_count' in counters:
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
            payroll_count = request.env['hr.payslip'].sudo().search_count([('employee_id', '=', emp.id)])
            values['payroll_count'] = payroll_count
        return values

    @http.route(['/my/payslips', '/my/payslips/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payslips(self, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        domain = [
            # ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '=', 'done')
        ]

        searchbar_sortings = {
            'date': {'label': _('Payslip Date'), 'payslip': 'date_from desc'},
            'name': {'label': _('Reference'), 'payslip': 'name'},
            'stage': {'label': _('Stage'), 'payslip': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['payslip']
        # content according to pager
        payslip_ids = request.env['hr.payslip'].sudo().search(domain, order=sort_order, limit=self._items_per_page)
        request.session['my_payslip_history'] = payslip_ids.ids[:100]

        values.update({
            'payslips': payslip_ids,
            'page_name': 'Payslips',
            'default_url': '/my/payslips',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("custom_portal_account_page.portal_my_payslips", values)

    def _payslip_get_page_view_values(self, payslip, access_token, **kwargs):
        values = {
            'payslip': payslip,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'employee_id': payslip.employee_id.id,
            'report_type': 'html',
            'action': request.env.ref('hr_payroll.action_view_hr_payslip_month_form'),
        }
        if payslip.company_id:
            values['res_company'] = payslip.company_id

        return values

    @http.route(['/my/payslips/<int:payslip>'], type='http', auth="user", website=True)
    def portal_payslip_page(self, payslip, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            payslip_sudo = self._document_check_access('hr.payslip', payslip, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=payslip_sudo, report_type=report_type,
                                     report_ref='hr_payroll.action_report_payslip', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if payslip_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % payslip_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % payslip_sudo.id] = now
                body = _('Payslip viewed by employee %s', payslip_sudo.employee_id.name)
                _message_post_helper(
                    "hr.payslip",
                    payslip_sudo.id,
                    body,
                    token=payslip_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=payslip_sudo.user_id.sudo().partner_id.ids,
                )

        values = self._payslip_get_page_view_values(payslip_sudo, access_token, **kw)
        values['message'] = message

        return request.render('custom_portal_account_page.payslip_portal_template', values)


class HrAttendance(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'attendance_count' in counters:
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
            attendance_count = request.env['attendance.sheet'].sudo().search_count([('employee_id', '=', emp.id)])
            values['attendance_count'] = attendance_count
        return values

    @http.route(['/my/attendances', '/my/attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendances(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        # content according to pager
        employee = request.env['hr.employee'].sudo().search([('user_id.partner_id', '=', partner.id)])
        attendance_ids = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee.id)],
                                                                    limit=self._items_per_page)
        request.session['my_attendance_history'] = attendance_ids.ids[:100]

        values.update({
            'attendances': attendance_ids,
            'page_name': 'My Attendance',
            'default_url': '/my/attendances',
        })
        return request.render("custom_portal_account_page.portal_my_attendances", values)

    @http.route(['/my/attendances_sheets', '/my/attendances_sheets/page/<int:page>'], type='http', auth="user",
                website=True)
    def portal_my_attendances_sheets(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        # content according to pager
        employee = request.env['hr.employee'].sudo().search([('user_id.partner_id', '=', partner.id)])
        attendance_sheet_ids = request.env['attendance.sheet'].sudo().search([('employee_id', '=', employee.id)],
                                                                             limit=self._items_per_page)
        request.session['my_attendance_sheet_history'] = attendance_sheet_ids.ids[:100]

        values.update({
            'attendances_sheets': attendance_sheet_ids,
            'page_name': 'My Attendance Sheet',
            'default_url': '/my/attendances_sheets',
        })
        return request.render("custom_portal_account_page.portal_my_attendances_sheets", values)
