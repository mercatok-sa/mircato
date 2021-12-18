# -*- coding: utf-8 -*-

import logging
from datetime import timedelta

import pytz
from odoo import api, fields, models, _

from odoo.osv.expression import AND

_logger = logging.getLogger(__name__)


class PosOrderReportWizard(models.TransientModel):
    _name = 'pos.order.report.wizard'
    _description = 'Point of Sale Order Report'

    def _default_start_date(self):
        """ Find the earliest start_date of the latests sessions """
        # restrict to configs available to the user
        config_ids = self.env['pos.config'].search([]).ids
        # exclude configs has not been opened for 2 days
        self.env.cr.execute("""
                SELECT
                max(start_at) as start,
                config_id
                FROM pos_session
                WHERE config_id = ANY(%s)
                AND start_at > (NOW() - INTERVAL '2 DAYS')
                GROUP BY config_id
            """, (config_ids,))
        latest_start_dates = [res['start'] for res in self.env.cr.dictfetchall()]
        # earliest of the latest sessions
        return latest_start_dates and min(latest_start_dates) or fields.Datetime.now()

    start_date = fields.Datetime(required=True, default=_default_start_date)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)
    pos_config_ids = fields.Many2many('pos.config', 'pos_order_report_configs',
                                      default=lambda s: s.env['pos.config'].search([]))

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

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
        # if config_ids:
        #     domain = AND([domain, [('config_id', 'in', config_ids)]])

        orders = self.env['pos.order'].search(domain)

        for config_id in config_ids:
            config_name = self.env['pos.config'].search([('id', '=', config_id)]).name
            orders_ids = orders.search([('config_id', '=', config_id)])

            sales_order_ids = orders_ids.filtered(lambda s: len(s.refunded_order_ids) == 0)
            sale_amount_with_tax = sum(sales_order_ids.mapped('amount_total'))

            # ضريبة المبيعات
            sale_order_tax = sum(sales_order_ids.mapped('amount_tax'))
            # المبيعات
            sale_order_amount = sale_amount_with_tax - sale_order_tax

            returns_order_ids = orders_ids.filtered(lambda s: len(s.refunded_order_ids) != 0)
            returns_amount_with_tax = sum(returns_order_ids.mapped('amount_total'))

            # ضريبة المردودات
            returns_order_tax = sum(returns_order_ids.mapped('amount_tax'))
            # المردودات
            returns_order_amount = returns_amount_with_tax - returns_order_tax

            # صافي المبيعات
            net_sales_amount = sale_order_amount + returns_order_amount
            # صافي الضريبة
            net_tax_amount = sale_order_tax + returns_order_tax

            payment_ids = orders_ids.mapped('payment_ids')

            # النقدية
            cash_payment = sum(payment_ids.filtered(lambda payment: payment.payment_method_id.name == "Cash").mapped('amount'))
            # ماستر كارد
            master_cart_payment = sum(payment_ids.filtered(lambda payment: payment.payment_method_id.name != "Cash").mapped('amount'))
            # الإجمالي
            total_payment = cash_payment + master_cart_payment

            # payment_ids = self.env["pos.payment"].search([('pos_order_id', 'in', orders.ids)]).ids
            # if payment_ids:
            #     self.env.cr.execute("""
            #         SELECT method.name, sum(amount) total
            #         FROM pos_payment AS payment,
            #              pos_payment_method AS method
            #         WHERE payment.payment_method_id = method.id
            #             AND payment.id IN %s
            #         GROUP BY method.name
            #     """, (tuple(payment_ids),))
            #     payments = self.env.cr.dictfetchall()
            # else:
            #     payments = []

            vals = {
                'config_name': config_name,
                'sale_order_amount': sale_order_amount,
                'returns_order_amount': returns_order_amount,
                'net_sales_amount': net_sales_amount,
                'sale_order_tax': sale_order_tax,
                'returns_order_tax': returns_order_tax,
                'net_tax_amount': net_tax_amount,
                'cash_payment': cash_payment,
                'master_cart_payment': master_cart_payment,
                'total_payment': total_payment,
            }
            res.append(vals)

        total_sale_order_amount = total_returns_order_amount = total_net_sales_amount = 0
        total_sale_order_tax = total_returns_order_tax = total_net_tax_amount = 0
        total_cash_payment = total_master_cart_payment = total_total_payment = 0

        for rec in res:
            total_sale_order_amount += rec['sale_order_amount']
            total_returns_order_amount += rec['returns_order_amount']
            total_net_sales_amount += rec['net_sales_amount']
            total_sale_order_tax += rec['sale_order_tax']
            total_returns_order_tax += rec['returns_order_tax']
            total_net_tax_amount += rec['net_tax_amount']
            total_cash_payment += rec['cash_payment']
            total_master_cart_payment += rec['master_cart_payment']
            total_total_payment += rec['total_payment']

        vals = {
            'config_name': 'Totals',
            'sale_order_amount': total_sale_order_amount,
            'returns_order_amount': total_returns_order_amount,
            'net_sales_amount': total_net_sales_amount,
            'sale_order_tax': total_sale_order_tax,
            'returns_order_tax': total_returns_order_tax,
            'net_tax_amount': total_net_tax_amount,
            'cash_payment': total_cash_payment,
            'master_cart_payment': total_master_cart_payment,
            'total_payment': total_total_payment,
        }
        res.append(vals)

        return res

    def get_resultat_pos_order_details(self):
        resultat = self.get_pos_order_details(self.start_date, self.end_date, self.pos_config_ids.ids)
        return resultat

    def generate_report(self):
        return self.env.ref('pos_order_report_details.template_point_of_sale_report_saledetails_new').report_action(self)


