# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.osv import expression
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request


class PortalAccount(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'penalty_count' in counters:
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
            penalty_count = request.env['penalty.request'].sudo().search_count([('employee_id', '=', emp.id)])
            values['penalty_count'] = penalty_count
        return values

    # ------------------------------------------------------------
    # My Invoices
    # ------------------------------------------------------------

    def _penalty_get_page_view_values(self, penalty, access_token, **kwargs):
        values = {
            'page_name': 'penalty',
            'penalty': penalty,
        }
        return self._get_page_view_values(penalty, access_token, values, 'my_penalties_history', False, **kwargs)

    def _get_penalty_searchbar_sortings(self):
        return {
            'date': {'label': _('Request Date'), 'order': 'request_date desc'},
            'name': {'label': _('Request Name'), 'order': 'name desc'},
            'type': {'label': _('Penalty Type'), 'order': 'penalty_type desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }

    def _get_penalty_searchbar_filters(self):
        return {
            'all': {'label': _('All'), 'domain': []},
            'penalty_by_amount': {'label': _('Penalty By Amount'), 'domain': [('penalty_type', '=', 'amount')]},
            'penalty_by_days': {'label': _('Penalty By Days'), 'domain': [('penalty_type', '=', 'days')]},
        }

    @http.route(['/my/penalties', '/my/penalties/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_penalties(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_my_penalties_values(page, date_begin, date_end, sortby, filterby)

        # pager
        pager = portal_pager(**values['pager'])

        # content according to pager and archive selected
        penalties = values['Penalties'](pager['offset'])
        request.session['my_penalties_history'] = penalties.ids[:100]

        values.update({
            'penalties': penalties,
            'pager': pager,
        })
        return request.render("employee_portal_penalty.portal_my_penalties", values)

    def _prepare_my_penalties_values(self, page, date_begin, date_end, sortby, filterby, domain=None,
                                    url="/my/penalties"):
        values = self._prepare_portal_layout_values()
        Penalties = request.env['penalty.request']
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)

        domain = expression.AND([
            domain or [],
            [('employee_id', '=', emp.id)],
        ])

        searchbar_sortings = self._get_penalty_searchbar_sortings()
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = self._get_penalty_searchbar_filters()
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('request_date', '>', date_begin), ('request_date', '<=', date_end)]

        values.update({
            'date': date_begin,
            # content according to pager and archive selected
            # lambda function to get the invoices recordset when the pager will be defined in the main method of a route
            'Penalties': lambda pager_offset: Penalties.search(domain, order=order, limit=self._items_per_page,
                                                                   offset=pager_offset),
            'page_name': 'penalty',
            'pager': {  # vals to define the pager.
                "url": url,
                "url_args": {'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
                "total": Penalties.sudo().search_count(domain),
                "page": page,
                "step": self._items_per_page,
            },
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return values

    @http.route(['/my/penalties/<int:penalty_id>'], type='http', auth="public", website=True)
    def portal_my_penalty_detail(self, penalty_id, access_token=None, report_type=None, download=False, **kw):
        try:
            penalty_sudo = self._document_check_access('penalty.request', penalty_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # if report_type in ('html', 'pdf', 'text'):
        #     return self._show_report(model=penalty_sudo, report_type=report_type, report_ref='account.account_invoices',
        #                              download=download)

        values = self._penalty_get_page_view_values(penalty_sudo, access_token, **kw)
        return request.render("employee_portal_penalty.portal_penalty_page", values)


    @http.route(['''/my/penalty/<model('penalty.request'):penalty>'''], type='http', auth="user", website=True)
    def portal_my_penalty(self, penalty, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1)
        # penalty_domain = ([('state', 'in', ['draft','confirmed'])])
        # holiday_type_ids = request.env['hr.leave.type'].sudo().search(penalty_domain)
        return request.render(
            "employee_portal_penalty.portal_my_penalty", {
                'penalty': penalty,
                'emp_id': emp and emp.id or False
            })

    # ------------------------------------------------------------
    # My Home
    # ------------------------------------------------------------

    # def details_form_validate(self, data, partner_creation=False):
    #     error, error_message = super(PortalAccount, self).details_form_validate(data)
    #     # prevent VAT/name change if invoices exist
    #     partner = request.env['res.users'].browse(request.uid).partner_id
    #     # Skip this test if we're creating a new partner as we won't ever block him from filling values.
    #     if not partner_creation and not partner.can_edit_vat():
    #         if 'vat' in data and (data['vat'] or False) != (partner.vat or False):
    #             error['vat'] = 'error'
    #             error_message.append(
    #                 _('Changing VAT number is not allowed once invoices have been issued for your account. Please contact us directly for this operation.'))
    #         if 'name' in data and (data['name'] or False) != (partner.name or False):
    #             error['name'] = 'error'
    #             error_message.append(
    #                 _('Changing your name is not allowed once invoices have been issued for your account. Please contact us directly for this operation.'))
    #         if 'company_name' in data and (data['company_name'] or False) != (partner.company_name or False):
    #             error['company_name'] = 'error'
    #             error_message.append(
    #                 _('Changing your company name is not allowed once invoices have been issued for your account. Please contact us directly for this operation.'))
    #     return error, error_message

    # def extra_details_form_validate(self, data, additional_required_fields, error, error_message):
    #     """ Ensure that all additional required fields have a value in the data """
    #     for field in additional_required_fields:
    #         if field.name not in data or not data[field.name]:
    #             error[field.name] = 'error'
    #             error_message.append(_('The field %s must be filled.', field.field_description.lower()))
    #     return error, error_message
