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

    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
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

        orders = self.env['pos.order'].search(domain)

        for config_id in config_ids:
            config_name = self.env['pos.config'].search([('id', '=', config_id)]).name
            orders_ids = orders.search([('config_id', '=', config_id)]).filtered(lambda o: o.date_order.date() >= date_start and o.date_order.date() <= date_stop)
            if orders_ids:
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

        if res:
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


