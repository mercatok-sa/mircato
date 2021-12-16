# -*- coding: utf-8 -*-

import logging
from datetime import timedelta

import pytz
from odoo import api, fields, models, _

from odoo.osv.expression import AND

_logger = logging.getLogger(__name__)


class PosDetailsInherit(models.TransientModel):
    _inherit = 'pos.details.wizard'

    @api.model
    def get_pos_order_details(self, date_start=False, date_stop=False, config_ids=False):
        res = []
        domain = [('state', 'in', ['paid', 'invoiced', 'done'])]

        if date_start:
            date_start = fields.Datetime.from_string(date_start)
        else:
            # start by default today 00:00:00
            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
            date_start = today.astimezone(pytz.timezone('UTC'))

        if date_stop:
            date_stop = fields.Datetime.from_string(date_stop)
            # avoid a date_stop smaller than date_start
            if (date_stop < date_start):
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)

        domain = AND([domain,
                      [('date_order', '>=', fields.Datetime.to_string(date_start)),
                       ('date_order', '<=', fields.Datetime.to_string(date_stop))]
                      ])
        if config_ids:
            domain = AND([domain, [('config_id', 'in', config_ids)]])

        orders = self.env['pos.order'].search(domain)

        for order in orders:
            print('line-----------------')
            customer = ''
            cash_payment = 0
            master_cart_payment = 0
            total = 0
            if order.partner_id:
                customer = order.partner_id.name
            print('1-----------', customer)
            if order.payment_ids:
                cash_payment = sum(order.payment_ids.filtered(lambda payment: payment.payment_method_id.name == "Cash").mapped('amount'))
                print('2-----------', cash_payment)
                master_cart_payment = sum(order.payment_ids.filtered(lambda payment: payment.payment_method_id.name != "Cash").mapped('amount'))
                print('3-----------', master_cart_payment)
                total = cash_payment + master_cart_payment
                print('4-----------', total)

            vals = {
                'customer': customer,

                'cash_payment': cash_payment,
                'master_cart_payment': master_cart_payment,
                'total': total,
            }
            res.append(vals)

        return res

    def get_resultat_pos_order_details(self):
        resultat = self.get_pos_order_details(self.start_date, self.end_date, self.pos_config_ids.ids)
        return resultat

    def print_report_new(self):
        return self.env.ref('era_pos_invoice.template_point_of_sale_report_saledetails_new').report_action(self)


