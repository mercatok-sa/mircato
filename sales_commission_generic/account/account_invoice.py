# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import api, fields, models, tools
from odoo.exceptions import UserError


class WizardInvoiceSaleCommission(models.Model):
    _name = 'wizard.invoice.sale.commission'
    _description = 'Wizard Invoice Sale Commission'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    salesperson = fields.Many2one('res.users', 'Sales Person', required=True)

    def print_commission_report(self):
        temp = []
        sale_invoice_commission_ids = self.env['invoice.sale.commission'].search(
            [('date', '>=', self.start_date), ('date', '<=', self.end_date), ('user_id', '=', self.salesperson.id)])
        if not sale_invoice_commission_ids:
            raise UserError('There Is No Any Commissions.')
        else:
            for a in sale_invoice_commission_ids:
                temp.append(a.id)
        data = temp
        datas = {
            'ids': self._ids,
            'model': 'invoice.sale.commission',
            'form': data,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'user': self.salesperson.name
        }
        return self.env.ref('sales_commission_generic.report_pdf').report_action(self, data=datas)


'''New class to handle sales commission in invoice.'''


class InvoiceSaleCommission(models.Model):
    _name = 'invoice.sale.commission'
    _description = 'Invoice Sale Commission'

    name = fields.Char(string="Description", size=512)
    type_name = fields.Char(string="Commission Name")
    comm_type = fields.Selection([
        ('standard', 'Standard'),
        ('partner', 'Partner Based'),
        ('mix', 'Product/Category/Margin Based'),
        ('discount', 'Discount Based'),
    ], 'Commission Type', copy=False, help="Select the type of commission you want to apply.")
    user_id = fields.Many2one('res.users', string='Sales Person',
                              help="sales person associated with this type of commission",
                              required=True)
    commission_amount = fields.Float(string="Commission Amount")
    invoice_id = fields.Many2one('account.move', string='Invoice Reference',
                                 help="Affected Invoice")
    order_id = fields.Many2one('sale.order', string='Order Reference',
                               help="Affected Sale Order")
    commission_id = fields.Many2one('sale.commission', string='Sale Commission',
                                    help="Related Commission", )
    product_id = fields.Many2one('product.product', string='Product',
                                 help="product", )
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_type = fields.Selection([('Affiliated Partner', 'Affiliated Partner'),
                                     ('Non-Affiliated Partner', 'Non-Affiliated Partner')], string='Partner Type')
    categ_id = fields.Many2one('product.category', string='Product Category')
    sub_categ_id = fields.Many2one('product.category', string='Product Sub-Category')
    date = fields.Date('Date')
    invoiced = fields.Boolean(string='Invoiced', readonly=True, default=False)


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    commission_ids = fields.One2many('invoice.sale.commission', 'invoice_id', string='Sales Commissions',
                                     help="Sale Commission related to this invoice(based on sales person)")

    def get_standard_commission(self, commission_brw, invoice):
        '''This method calculates standard commission if any exception is not found for any product line.
           @return : Id of created commission record.'''
        invoice_commission_ids = []
        invoice_commission_obj = self.env['invoice.sale.commission']
        if invoice.move_type == 'out_invoice':
            for line in invoice.invoice_line_ids:
                amount = line.price_subtotal
                standard_commission_amount = amount * (commission_brw.standard_commission / 100)
                name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' ( ' + tools.ustr(
                    commission_brw.standard_commission) + '%)" for product "' + tools.ustr(line.product_id.name) + '"'
                standard_invoice_commission_data = {
                    'name': name,
                    'user_id': invoice.user_id.id,
                    'commission_id': commission_brw.id,
                    'product_id': line.product_id.id,
                    'type_name': commission_brw.name,
                    'comm_type': commission_brw.comm_type,
                    'commission_amount': standard_commission_amount,
                    'invoice_id': invoice.id,
                    'date': datetime.datetime.today()}
                invoice_commission_ids.append(invoice_commission_obj.create(standard_invoice_commission_data))
        elif invoice.move_type == 'out_refund':
            for line in invoice.invoice_line_ids:
                amount = line.price_subtotal
                standard_commission_amount = (amount * (commission_brw.standard_commission / 100)) * -1
                name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' ( ' + tools.ustr(
                    commission_brw.standard_commission) + '%)" for product "' + tools.ustr(line.product_id.name) + '"'
                standard_invoice_commission_data = {
                    'name': name,
                    'user_id': invoice.user_id.id,
                    'commission_id': commission_brw.id,
                    'product_id': line.product_id.id,
                    'type_name': commission_brw.name,
                    'comm_type': commission_brw.comm_type,
                    'commission_amount': standard_commission_amount,
                    'invoice_id': invoice.id,
                    'date': datetime.datetime.today()}
                invoice_commission_ids.append(invoice_commission_obj.create(standard_invoice_commission_data))
        return invoice_commission_ids

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

    def get_partner_commission(self, commission_brw, invoice):
        '''This method calculates commission for Partner Based.
           @return : List of ids for commission records created.'''
        invoice_commission_ids = []
        commission_precentage = commission_brw.standard_commission
        invoice_commission_obj = self.env['invoice.sale.commission']
        exception_obj = self.env['sale.commission.exception']
        sales_person_list = [x.id for x in commission_brw.user_ids]
        if invoice.move_type == 'out_invoice':
            for line in invoice.invoice_line_ids:
                amount = line.price_subtotal
                invoice_commission_data = {}
                exception_ids = self.get_exceptions(line, commission_brw)
                margin = ((line.price_subtotal / line.quantity) - line.product_id.standard_price)
                # ================================================================================
                cost = line.product_id.standard_price
                if cost == 0.0:
                    actual_margin_percentage = (margin * 100) / 1.0  # if Product cost is not given
                else:
                    actual_margin_percentage = (margin * 100) / line.product_id.standard_price
                # ================================================================================
                # actual_margin_percentage = (margin * 100) / line.product_id.standard_price
                if line.sol_id:
                    margin = ((line.price_subtotal / line.quantity) - line.sol_id.purchase_price)
                    # ================================================================================
                    cost_line = line.sol_id.purchase_price
                    if cost_line == 0.0:
                        actual_margin_percentage = (margin * 100) / 1.0  # if purchase price is not given in order lines
                    else:
                        actual_margin_percentage = (margin * 100) / line.sol_id.purchase_price
                # ================================================================================
                # actual_margin_percentage = (margin * 100) / line.sol_id.purchase_price
                if (
                        invoice.user_id and invoice.user_id.id in sales_person_list) and invoice.partner_id.is_affiliated == True:
                    commission_amount = amount * (commission_brw.affiliated_partner_commission / 100)
                    name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
                        commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
                        invoice.partner_id.name) + '"'
                    invoice_commission_data = {'name': name,
                                               'user_id': invoice.user_id.id,
                                               'partner_id': invoice.partner_id.id,
                                               'commission_id': commission_brw.id,
                                               'type_name': commission_brw.name,
                                               'comm_type': commission_brw.comm_type,
                                               'partner_type': 'Affiliated Partner',
                                               'commission_amount': commission_amount,
                                               'invoice_id': invoice.id,
                                               'date': datetime.datetime.today()}
                elif (
                        invoice.user_id and invoice.user_id.id in sales_person_list) and invoice.partner_id.is_affiliated == False:
                    commission_amount = amount * (commission_brw.nonaffiliated_partner_commission / 100)
                    name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
                        commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
                        invoice.partner_id.name) + '"'
                    invoice_commission_data = {'name': name,
                                               'user_id': invoice.user_id.id,
                                               'partner_id': invoice.partner_id.id,
                                               'commission_id': commission_brw.id,
                                               'type_name': commission_brw.name,
                                               'comm_type': commission_brw.comm_type,
                                               'partner_type': 'Non-Affiliated Partner',
                                               'commission_amount': commission_amount,
                                               'invoice_id': invoice.id,
                                               'date': datetime.datetime.today()}
                if invoice_commission_data:
                    invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
        elif invoice.move_type == 'out_refund':
            for line in invoice.invoice_line_ids:
                amount = line.price_subtotal
                invoice_commission_data = {}
                exception_ids = self.get_exceptions(line, commission_brw)
                margin = ((line.price_subtotal / line.quantity) - line.product_id.standard_price)
                actual_margin_percentage = (margin * 100) / line.product_id.standard_price
                if line.sol_id:
                    margin = ((line.price_subtotal / line.quantity) - line.sol_id.purchase_price)
                    actual_margin_percentage = (margin * 100) / line.sol_id.purchase_price
                if (
                        invoice.user_id and invoice.user_id.id in sales_person_list) and invoice.partner_id.is_affiliated == True:
                    commission_amount = (amount * (commission_brw.affiliated_partner_commission / 100)) * -1
                    name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
                        commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
                        invoice.partner_id.name) + '"'
                    invoice_commission_data = {'name': name,
                                               'user_id': invoice.user_id.id,
                                               'partner_id': invoice.partner_id.id,
                                               'commission_id': commission_brw.id,
                                               'type_name': commission_brw.name,
                                               'comm_type': commission_brw.comm_type,
                                               'partner_type': 'Affiliated Partner',
                                               'commission_amount': commission_amount,
                                               'invoice_id': invoice.id,
                                               'date': datetime.datetime.today()}
                elif (
                        invoice.user_id and invoice.user_id.id in sales_person_list) and invoice.partner_id.is_affiliated == False:
                    commission_amount = (amount * (commission_brw.nonaffiliated_partner_commission / 100)) * -1
                    name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
                        commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
                        invoice.partner_id.name) + '"'
                    invoice_commission_data = {'name': name,
                                               'user_id': invoice.user_id.id,
                                               'partner_id': invoice.partner_id.id,
                                               'commission_id': commission_brw.id,
                                               'type_name': commission_brw.name,
                                               'comm_type': commission_brw.comm_type,
                                               'partner_type': 'Non-Affiliated Partner',
                                               'commission_amount': commission_amount,
                                               'invoice_id': invoice.id,
                                               'date': datetime.datetime.today()}
                if invoice_commission_data:
                    invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
        return invoice_commission_ids

    # ===========================================================================================================
    def get_discount_commission(self, commission_brw, invoice):
        '''This method calculates commission for Discount Based Rules.
           @return : List of ids for commission records created.'''
        invoice_commission_ids = []
        invoice_commission_obj = self.env['invoice.sale.commission']
        for line in invoice.invoice_line_ids:
            amount = line.price_subtotal
            invoice_commission_data = {}
            commission_percentage = 0.0
            commission_amount = 0.0
            name = ''
            sol_discount = line.sol_id.discount
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
                                       'user_id': invoice.user_id.id,
                                       'commission_id': commission_brw.id,
                                       'product_id': line.product_id.id,
                                       'type_name': commission_brw.name,
                                       'comm_type': commission_brw.comm_type,
                                       'commission_amount': commission_amount,
                                       'invoice_id': invoice.id,
                                       'date': datetime.datetime.today()}
            if invoice_commission_data:
                invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
        return invoice_commission_ids

    # ===========================================================================================================

    def get_mix_commission(self, commission_brw, invoice):
        '''This method calculates commission for Product/Category/Margin Based.
           @return : List of ids for commission records created.'''
        exception_obj = self.env['sale.commission.exception']
        invoice_commission_obj = self.env['invoice.sale.commission']
        invoice_commission_ids = []
        if invoice.move_type == 'out_invoice':
            for line in invoice.invoice_line_ids:
                amount = line.price_subtotal
                invoice_commission_data = {}
                exception_ids = []
                if not line.product_id: continue
                margin = ((line.price_subtotal / line.quantity) - line.product_id.standard_price)
                amount = margin * line.quantity
                # ================================================================================
                cost = line.product_id.standard_price
                if cost == 0.0:
                    actual_margin_percentage = (margin * 100) / 1.0  # if Product cost is not given
                else:
                    actual_margin_percentage = (margin * 100) / line.product_id.standard_price
                # ================================================================================
                if line.sol_id:
                    margin = ((line.price_subtotal / line.quantity) - line.sol_id.purchase_price)
                    # ================================================================================
                    cost_line = line.sol_id.purchase_price
                    if cost_line == 0.0:
                        actual_margin_percentage = (margin * 100) / 1.0  # if purchase price is not given in order lines
                    else:
                        actual_margin_percentage = (margin * 100) / line.sol_id.purchase_price
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
                                               'user_id': invoice.user_id.id,
                                               'type_name': commission_brw.name,
                                               'comm_type': commission_brw.comm_type,
                                               'commission_amount': commission_amount,
                                               'invoice_id': invoice.id,
                                               'date': datetime.datetime.today()}
                    invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
        elif invoice.move_type == 'out_refund':
            for line in invoice.invoice_line_ids:
                amount = line.price_subtotal
                invoice_commission_data = {}
                exception_ids = []
                if not line.product_id: continue
                margin = ((line.price_subtotal / line.quantity) - line.product_id.standard_price)
                # ================================================================================
                cost = line.product_id.standard_price
                if cost == 0.0:
                    actual_margin_percentage = (margin * 100) / 1.0  # if Product cost is not given
                else:
                    actual_margin_percentage = (margin * 100) / line.product_id.standard_price
                # ================================================================================
                if line.sol_id:
                    margin = ((line.price_subtotal / line.quantity) - line.sol_id.purchase_price)
                    # ================================================================================
                    cost_line = line.sol_id.purchase_price
                    if cost_line == 0.0:
                        actual_margin_percentage = (margin * 100) / 1.0  # if purchase price is not given in order lines
                    else:
                        actual_margin_percentage = (margin * 100) / line.sol_id.purchase_price
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
                    commission_amount = (amount * (commission_precentage / 100)) * -1
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
                                               'user_id': invoice.user_id.id,
                                               'type_name': commission_brw.name,
                                               'comm_type': commission_brw.comm_type,
                                               'commission_amount': commission_amount,
                                               'invoice_id': invoice.id,
                                               'date': datetime.datetime.today()}
                    invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
        return invoice_commission_ids

    def get_sales_commission(self):
        '''This is control method for calculating commissions(called from workflow).
           @return : List of ids for commission records created.'''
        invoice_commission_ids = []
        for invoice in self:
            if invoice.user_id and invoice.move_type == 'out_invoice':
                commission_obj = self.env['sale.commission']
                commission_id = commission_obj.search([('user_ids', 'in', invoice.user_id.id)])
                if not commission_id:
                    return False
                else:
                    commission_id = commission_id[0]
                commission_brw = commission_id

                if commission_brw.comm_type == 'mix':
                    invoice_commission_ids = self.get_mix_commission(commission_brw, invoice)
                elif commission_brw.comm_type == 'partner':
                    invoice_commission_ids = self.get_partner_commission(commission_brw, invoice)
                elif commission_brw.comm_type == 'discount':
                    invoice_commission_ids = self.get_discount_commission(commission_brw, invoice)
                else:
                    invoice_commission_ids = self.get_standard_commission(commission_brw, invoice)
            elif invoice.user_id and invoice.move_type == 'out_refund':
                commission_obj = self.env['sale.commission']
                commission_id = commission_obj.search([('user_ids', 'in', invoice.user_id.id)])
                if not commission_id:
                    return False
                else:
                    commission_id = commission_id[0]
                commission_brw = commission_id

                if commission_brw.comm_type == 'mix':
                    invoice_commission_ids = self.get_mix_commission(commission_brw, invoice)
                elif commission_brw.comm_type == 'partner':
                    invoice_commission_ids = self.get_partner_commission(commission_brw, invoice)
                elif commission_brw.comm_type == 'discount':
                    invoice_commission_ids = self.get_discount_commission(commission_brw, invoice)
                else:
                    invoice_commission_ids = self.get_standard_commission(commission_brw, invoice)
        return invoice_commission_ids

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        for move in self:

            if move.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id

            # Compute 'payment_state'.
            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':
                if currency.is_zero(move.amount_residual):
                    if all(payment.is_matched for payment in move._get_reconciled_payments()):
                        new_pmt_state = 'paid'


                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                        commission_configuration = self.env.user.company_id.commission_configuration
                        if commission_configuration == 'payment':
                            move.get_sales_commission()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                reverse_moves = self.env['account.move'].search(
                    [('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (
                        reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            move.payment_state = new_pmt_state

    def action_post(self):
        res = super(AccountInvoice, self).action_post()
        commission_configuration = self.env.user.company_id.commission_configuration
        if commission_configuration == 'invoice':
            self.get_sales_commission()
        return res

    def button_draft(self):
        res = super(AccountInvoice, self).button_draft()
        for mv in self:
            if mv.commission_ids:
                mv.commission_ids.sudo().unlink()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    sol_id = fields.Many2one('sale.order.line', string='Sales Order Line')
