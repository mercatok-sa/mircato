# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii
from datetime import date

from odoo import fields, http, _
# from odoo.exceptions import AccessError, MissingError
from odoo.http import request
# from odoo.addons.payment.controllers.portal import PaymentProcessing
# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
# from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id



        return values

    #
    # Quotations and Sales Orders
    #

    @http.route(['/qr/pos_order', '/qr/pos_order/page/<int:page>'], type='http', auth="user", website=True)
    def portal_qr_pos_order(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel'])
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_quotations", values)


    @http.route(['/qr/pos_order/<int:order_id>'], type='http', auth="public", website=True)
    def portal_qr_posorder_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        print('portal_qr_posorder_page')
        values={'sales_user': False, 'page_name': 'POS Order', 'archive_groups': [],  }

        if order_id:
            print(order_id)
            POSOrder = request.env['pos.order']
            order=POSOrder.sudo().search([('id','=',order_id)])
            print(order)
            # values = self._prepare_portal_layout_values()
            print(values)
            values.update({'pos_order':order[0]})
            return request.render('qerp_whatsapp_pos.pos_order_portal_template',values )


