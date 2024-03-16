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

    def get_domain_my_resignation(self, user):
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        return [('employee_id', '=', emp and emp.id or False)]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'reg_count' in counters:
            emp = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
            reg_count = request.env['hr.resignation.request'].sudo().search_count([('employee_id', '=', emp.id)])
            values['reg_count'] = reg_count
        return values

    @http.route(['/my/resignation', '/my/resignation/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_resignation(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, groupby='none',
                              **kw):
        values = self._prepare_portal_layout_values()
        HrReg = request.env['hr.resignation.request']
        resignation_sudo = request.env['hr.resignation.request'].sudo()
        domain = self.get_domain_my_resignation(request.env.user)

        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

        # fileter  By
        searchbar_filters = {
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'resigned': {'label': _('Resigned'), 'domain': [('state', '=', 'resigned')]},
            'canceled': {'label': _('Canceled'), 'domain': [('state', '=', 'canceled')]},

        }
        # sort By
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        # group By
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'reg': {'input': 'regs', 'label': _('Reg State')},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'draft'
        domain += searchbar_filters[filterby]['domain']
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # pager
        reg_count = HrReg.search_count(domain)
        pager = request.website.pager(
            url="/my/resignation",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=reg_count,
            page=page,
            step=self._items_per_page
        )
        # default groupby
        if groupby == 'regs':
            order = "employee_id, %s" % order
        # content according to pager and archive selected
        resignation = HrReg.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'none':
            grouped_reg = []
            if resignation:
                grouped_reg = [resignation]
        else:
            grouped_reg = [resignation_sudo.concat(*g) for k, g in groupbyelem(resignation, itemgetter('employee_id'))]

        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1)
        values.update({
            'date': date_begin,
            'resignation': resignation,
            'grouped_reg': grouped_reg,
            'page_name': 'resignation',
            'emp_id': emp and emp.id or False,
            'emp_name': emp and emp.name or False,
            'default_url': '/my/resignation',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })
        return request.render("hr_customization.portal_my_reg_details", values)

    @http.route(['''/my/resignation/<model('hr.resignation.request'):resignation>'''], type='http', auth="user",
                website=True)
    def portal_my_resignation_reg(self, resignation, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],
                                                       limit=1)
        return request.render(
            "hr_customization.portal_my_reg_edit", {
                'resignation': resignation,
                'emp_id': emp and emp.id or False,
                'current_emp': request.env.user.employee_id.name
            })
