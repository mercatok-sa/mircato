# See LICENSE file for full copyright and licensing details

from collections import OrderedDict
from operator import itemgetter
from odoo import fields
from odoo import http
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.translate import _


class WebsiteAccount(CustomerPortal):

    def get_domain_my_leaves(self, user):
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1)
        return [
            ('employee_id', '=', emp and emp.id or False),
        ]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'leave_count' in counters:
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
            leave_count = request.env['hr.leave'].sudo().search_count([('employee_id', '=', emp.id)])
            values['leave_count'] = leave_count
        return values

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_leaves(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, groupby='none',
                         **kw):
        values = self._prepare_portal_layout_values()
        HrLeave = request.env['hr.leave'].sudo()
        Timeoff_sudo = request.env['hr.leave'].sudo()
        domain = self.get_domain_my_leaves(request.env.user)

        holiday_domain = ([('virtual_remaining_leaves', '>', 0), ('max_leaves', '>', '0')])
        holiday_type_ids = request.env['hr.leave.type'].sudo().search(holiday_domain)
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1)
        values.update({
            'holiday_types': holiday_type_ids.with_context({'employee_id': emp and emp.id or False}).name_get(),
            'delegations': request.env['hr.employee'].sudo().search(
                [('company_id', '=', request.env.company.id)]) or False,
            'delegation_required': emp.delegation_required})
        # fileter  By
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'confirm': {'label': _('To Approve'), 'domain': [('state', '=', 'confirm')]},
            'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]},
            'validate1': {'label': _('Second Approval'), 'domain': [('state', '=', 'validate1')]},
            'validate': {'label': _('Approved'), 'domain': [('state', '=', 'validate')]},
        }
        # sort By
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        # group By
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'timeoff': {'input': 'timeoff', 'label': _('Time Off Type')},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # pager
        leave_count = HrLeave.search_count(domain)
        pager = request.website.pager(
            url="/my/leaves",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=leave_count,
            page=page,
            step=self._items_per_page
        )
        # default groupby
        if groupby == 'timeoff':
            order = "holiday_status_id, %s" % order
        # content according to pager and archive selected
        leaves = HrLeave.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'none':
            grouped_timeoff = []
            if leaves:
                grouped_timeoff = [leaves]
        else:
            grouped_timeoff = [Timeoff_sudo.concat(*g) for k, g in groupbyelem(leaves, itemgetter('holiday_status_id'))]
        values.update({
            'date': date_begin,
            'leaves': leaves,
            'grouped_timeoff': grouped_timeoff,
            'page_name': 'leave',
            'default_url': '/my/leaves',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })
        return request.render("employee_portal_timeoff.portal_my_leaves_details", values)

    @http.route(['''/my/timeoff/<model('hr.leave'):timeoff>'''], type='http', auth="user", website=True)
    def portal_my_timeoff(self, timeoff, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1)
        holiday_domain = ([('virtual_remaining_leaves', '>', 0), ('max_leaves', '>', '0')])
        holiday_type_ids = request.env['hr.leave.type'].sudo().search(holiday_domain)
        return request.render(
            "employee_portal_timeoff.portal_my_timeoff", {
                'timeoff': timeoff,
                'holiday_types': holiday_type_ids.with_context({'employee_id': emp and emp.id or False}).name_get(),
                'emp_id': emp and emp.id or False
            })

    @http.route(['/my/leaves/summary'], type='http', auth="user", website=True)
    def leaves_summary(self):
        get_days_all_request = request.env['hr.leave.type'].sudo().get_days_all_request()
        return request.render(
            "employee_portal_timeoff.my_leaves_summary", {
                'timeoffs': get_days_all_request})
