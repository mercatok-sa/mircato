# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    ecr_number = fields.Char()

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['ecr_number'] = ui_order.get('ecr_number')
        print(order_fields)
        return order_fields

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        payment_fields = super(PosOrder, self)._payment_fields(order, ui_paymentline)
        payment_fields['PrimaryAccountNumber'] = ui_paymentline.get('PrimaryAccountNumber')
        payment_fields['RetrievalReferenceNumber'] = ui_paymentline.get('RetrievalReferenceNumber')
        payment_fields['TransactionAuthCode'] = ui_paymentline.get('TransactionAuthCode')
        return payment_fields
