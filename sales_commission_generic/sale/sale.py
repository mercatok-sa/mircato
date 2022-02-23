# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import fields, models
from odoo import tools


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commission_ids = fields.One2many('invoice.sale.commission', 'order_id', string='Sales Commissions',
                                     help="Sale Commission related to this order(based on sales person)")

    def get_exceptions(self, line, commission_brw):
        '''This method searches exception for any product line.
           @return : List of ids for all exception for particular product line.'''
        exception_obj = self.env['sale.commission.exception']
        categ_obj = self.env['product.category']
        product_exception_id = exception_obj.search([
            ('product_id', '=', line.product_id.id),
            ('commission_id', '=', commission_brw.id),
            ('based_on', '=', 'Products')
        ])

        if product_exception_id:
            return product_exception_id
        subcateg_exception_id = exception_obj.search([
            ('category_store', 'in', line.product_id.categ_id.id),
            ('commission_id', '=', commission_brw.id),
            ('based_on', '=', 'Product Sub-Categories')])

        if subcateg_exception_id:
            return subcateg_exception_id

        exclusive_categ_exception_id = exception_obj.search([
            ('category_store', 'in', line.product_id.categ_id.id),
            ('commission_id', '=', commission_brw.id),
            ('based_on', '=', 'Product Categories'),
        ])

        if exclusive_categ_exception_id:
            return exclusive_categ_exception_id
        return []

    # ============================================================================================================================
    def get_discount_commission(self, commission_brw, order):
        '''This method calculates commission for Discount Based Rules.
           @return : List of ids for commission records created.'''
        invoice_commission_ids = []
        invoice_commission_obj = self.env['invoice.sale.commission']
        for line in order.order_line:
            amount = line.price_subtotal
            invoice_commission_data = {}
            commission_percentage = 0.0
            commission_amount = 0.0
            name = ''
            sol_discount = line.discount
            if sol_discount == 0.0:
                commission_percentage = commission_brw.no_discount_commission_percentage
            elif sol_discount > commission_brw.max_discount_commission_percentage:
                commission_percentage = commission_brw.gt_discount_commission_percentage
            else:
                for rule in commission_brw.rule_ids:
                    if rule.discount_percentage == sol_discount:
                        commission_percentage = rule.commission_percentage
            commission_amount = amount * (commission_percentage / 100)
            name = 'Discount Based commission for ' + ' (' + tools.ustr(
                sol_discount) + ' %) discount is ' + ' (' + tools.ustr(commission_percentage) + '%) commission"'
            invoice_commission_data = {'name': name,
                                       'user_id': order.user_id.id,
                                       'commission_id': commission_brw.id,
                                       'product_id': line.product_id.id,
                                       'type_name': commission_brw.name,
                                       'comm_type': commission_brw.comm_type,
                                       'commission_amount': commission_amount,
                                       'order_id': order.id,
                                       'date': datetime.datetime.today()}
            if invoice_commission_data:
                invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
        return invoice_commission_ids

    # ============================================================================================================================

    def get_mix_commission(self, commission_brw, order):
        '''This method calculates commission for Product/Category/Margin Based.
           @return : List of ids for commission records created.'''
        exception_obj = self.env['sale.commission.exception']
        invoice_commission_obj = self.env['invoice.sale.commission']
        invoice_commission_ids = []
        for line in order.order_line:
            amount = line.price_subtotal
            invoice_commission_data = {}
            exception_ids = []
            if not line.product_id: continue
            margin = ((line.price_subtotal / line.product_uom_qty) - line.product_id.standard_price)
            # ================================================================================
            cost = line.product_id.standard_price
            if cost == 0.0:
                actual_margin_percentage = (margin * 100) / 1.0  # if Product cost is not given
            else:
                actual_margin_percentage = (margin * 100) / line.product_id.standard_price
            # ================================================================================
            margin = ((line.price_subtotal / line.product_uom_qty) - line.purchase_price)

            amount = margin * line.product_uom_qty
            # ================================================================================
            cost_line = line.purchase_price
            if cost_line == 0.0:
                actual_margin_percentage = (margin * 100) / 1.0  # if purchase price is not given in order lines
            else:
                actual_margin_percentage = (margin * 100) / line.purchase_price
            # ================================================================================
            exception_ids = self.get_exceptions(line, commission_brw)

            for exception in exception_ids:
                product_id = False
                categ_id = False
                sub_categ_id = False
                commission_precentage = commission_brw.standard_commission
                name = ''
                margin_percentage = exception.margin_percentage
                if exception.based_on_2 == 'Margin' and actual_margin_percentage > margin_percentage:
                    commission_precentage = exception.above_margin_commission
                elif exception.based_on_2 == 'Margin' and actual_margin_percentage <= margin_percentage:
                    commission_precentage = exception.below_margin_commission
                elif exception.based_on_2 == 'Commission Exception':
                    commission_precentage = exception.commission_precentage
                elif exception.based_on_2 == 'Fix Price' and line.price_unit >= exception.price:
                    commission_precentage = exception.price_percentage
                elif exception.based_on_2 == 'Fix Price' and line.price_unit < exception.price:
                    pass
                commission_amount = amount * (commission_precentage / 100)
                if exception.based_on == 'Products':
                    product_id = exception.product_id.id
                    name = 'Commission Exception for ' + tools.ustr(exception.based_on) + ' "' + tools.ustr(
                        exception.product_id.name) + '" @' + tools.ustr(commission_precentage) + '%'
                elif exception.based_on == 'Product Categories':
                    categ_id = exception.categ_id.id
                    name = 'Commission Exception for ' + tools.ustr(exception.based_on) + ' "' + tools.ustr(
                        exception.categ_id.name) + '" @' + tools.ustr(commission_precentage) + '%'
                elif exception.based_on == 'Product Sub-Categories':
                    sub_categ_id = exception.sub_categ_id.id
                    name = 'Commission Exception for ' + tools.ustr(exception.based_on) + ' "' + tools.ustr(
                        exception.sub_categ_id.name) + '" @' + tools.ustr(commission_precentage) + '%'
                invoice_commission_data = {'name': name,
                                           'product_id': product_id or False,
                                           'commission_id': commission_brw.id,
                                           'categ_id': categ_id or False,
                                           'sub_categ_id': sub_categ_id or False,
                                           'user_id': order.user_id.id,
                                           'type_name': commission_brw.name,
                                           'comm_type': commission_brw.comm_type,
                                           'commission_amount': commission_amount,
                                           'order_id': order.id,
                                           'date': datetime.datetime.today()}
                invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
        return invoice_commission_ids

    def get_partner_commission(self, commission_brw, order):
        '''This method calculates commission for Partner Based.
           @return : List of ids for commission records created.'''
        invoice_commission_ids = []
        invoice_commission_obj = self.env['invoice.sale.commission']
        sales_person_list = [x.id for x in commission_brw.user_ids]
        for line in order.order_line:
            amount = line.price_subtotal
            invoice_commission_data = {}
            if (order.user_id and order.user_id.id in sales_person_list) and order.partner_id.is_affiliated == True:
                commission_amount = amount * (commission_brw.affiliated_partner_commission / 100)
                name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
                    commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
                    order.partner_id.name) + '"'
                invoice_commission_data = {'name': name,
                                           'user_id': order.user_id.id,
                                           'partner_id': order.partner_id.id,
                                           'commission_id': commission_brw.id,
                                           'type_name': commission_brw.name,
                                           'comm_type': commission_brw.comm_type,
                                           'partner_type': 'Affiliated Partner',
                                           'commission_amount': commission_amount,
                                           'order_id': order.id,
                                           'date': datetime.datetime.today()}
            elif (order.user_id and order.user_id.id in sales_person_list) and order.partner_id.is_affiliated == False:
                commission_amount = amount * (commission_brw.nonaffiliated_partner_commission / 100)
                name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
                    commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
                    order.partner_id.name) + '"'
                invoice_commission_data = {'name': name,
                                           'user_id': order.user_id.id,
                                           'partner_id': order.partner_id.id,
                                           'commission_id': commission_brw.id,
                                           'type_name': commission_brw.name,
                                           'comm_type': commission_brw.comm_type,
                                           'partner_type': 'Non-Affiliated Partner',
                                           'commission_amount': commission_amount,
                                           'order_id': order.id,
                                           'date': datetime.datetime.today()}
            if invoice_commission_data:
                invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
        return invoice_commission_ids

    def get_standard_commission(self, commission_brw, order):
        '''This method calculates standard commission if any exception is not found for any product line.
           @return : Id of created commission record.'''
        invoice_commission_ids = []
        invoice_commission_obj = self.env['invoice.sale.commission']
        for line in order.order_line:
            amount = line.price_subtotal
            standard_commission_amount = amount * (commission_brw.standard_commission / 100)
            name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' ( ' + tools.ustr(
                commission_brw.standard_commission) + '%)" for product "' + tools.ustr(line.product_id.name) + '"'
            standard_invoice_commission_data = {
                'name': name,
                'user_id': order.user_id.id,
                'commission_id': commission_brw.id,
                'product_id': line.product_id.id,
                'type_name': commission_brw.name,
                'comm_type': commission_brw.comm_type,
                'commission_amount': standard_commission_amount,
                'order_id': order.id,
                'date': datetime.datetime.today()}
            invoice_commission_ids.append(invoice_commission_obj.create(standard_invoice_commission_data))
        return invoice_commission_ids

    def get_sales_commission(self):
        '''This is control method for calculating commissions(called from workflow).
           @return : List of ids for commission records created.'''
        for order in self:
            invoice_commission_ids = []
            if order.user_id:
                commission_obj = self.env['sale.commission']
                commission_id = commission_obj.search([('user_ids', 'in', order.user_id.id)])
                if not commission_id:
                    return False
                else:
                    commission_id = commission_id[0]
                commission_brw = commission_id

                if commission_brw.comm_type == 'mix':

                    invoice_commission_ids = self.get_mix_commission(commission_brw, order)
                elif commission_brw.comm_type == 'partner':
                    invoice_commission_ids = self.get_partner_commission(commission_brw, order)
                elif commission_brw.comm_type == 'discount':
                    invoice_commission_ids = self.get_discount_commission(commission_brw, order)
                else:
                    invoice_commission_ids = self.get_standard_commission(commission_brw, order)
        return invoice_commission_ids

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        commission_configuration = self.env.user.company_id.commission_configuration
        if commission_configuration == 'sale_order':
            self.get_sales_commission()
        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for so in self:
            if so.commission_ids:
                so.commission_ids.sudo().unlink()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({'sol_id': self.id})
        return res
