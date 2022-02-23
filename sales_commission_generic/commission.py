# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError


class CreateCommisionInvoice(models.Model):
    _name = 'create.invoice.commission'
    _description = 'create invoice commission'

    group_by = fields.Boolean('Group By', readonly=False)
    date = fields.Date('Invoice Date', readonly=False)

    def invoice_create(self):
        sale_invoice_ids = self.env['invoice.sale.commission'].browse(self._context.get('active_ids'))
        if any(line.invoiced == True for line in sale_invoice_ids):
            raise UserError('Invoiced Lines cannot be Invoiced Again.')

        commission_discount_account = self.env.user.company_id.commission_discount_account
        if not commission_discount_account:
            raise UserError('You have not configured commission Discount Account')

        moves = []
        if self.group_by:
            group_dict = {}
            for record in sale_invoice_ids:
                group_dict.setdefault(record.user_id.name, []).append(record)
            for dict_record in group_dict:
                inv_lines = []
                for inv_record in group_dict.get(dict_record):
                    inv_lines.append({
                        'name': inv_record.name,
                        'quantity': 1,
                        'price_unit': inv_record.commission_amount,
                    })
                partner = self.env['res.partner'].search([('name', '=', dict_record)])
                inv_id = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': partner.id,
                    'invoice_date': self.date if self.date else datetime.datetime.today().date(),
                    'invoice_line_ids': [(0, 0, l) for l in inv_lines],
                })
                moves.append(inv_id.id)
            sale_invoice_ids.write({'invoiced': True})

        else:

            for commission_record in sale_invoice_ids:
                inv_lines = []
                inv_lines.append({
                    'name': commission_record.name,
                    'quantity': 1,
                    'price_unit': commission_record.commission_amount,
                })

                inv_id = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'invoice_line_ids': [(0, 0, l) for l in inv_lines],
                    'partner_id': commission_record.user_id.partner_id.id,
                    'invoice_date': self.date if self.date else datetime.datetime.today().date()
                })
                moves.append(inv_id.id)
            sale_invoice_ids.write({'invoiced': True})


'''New class to handle sales commission configuration.'''


class SaleCommission(models.Model):
    _name = 'sale.commission'
    _rec_name = 'comm_type'
    _description = 'Sale commission'

    user_ids = fields.Many2many('res.users', 'commision_rel_user', 'commision_id', 'user_id', string='Sales Person',
                                help="Select sales person associated with this type of commission",
                                required=True)
    name = fields.Char('Commission Name', required=True)
    comm_type = fields.Selection([
        ('standard', 'Standard'),
        ('partner', 'Partner Based'),
        ('mix', 'Product/Category/Margin Based'),
        ('discount', 'Discount Based'),
    ], 'Commission Type', copy=False, default='standard', help="Select the type of commission you want to apply.")
    affiliated_partner_commission = fields.Float(string="Affiliated Partner Commission percentage")
    nonaffiliated_partner_commission = fields.Float(string="Non-Affiliated Partner Commission percentage")
    exception_ids = fields.One2many('sale.commission.exception', 'commission_id', string='Sales Commission Exceptions',
                                    help="Sales commission exceptions",
                                    )
    rule_ids = fields.One2many('discount.commission.rules', 'commission_id', string='Commission Rules',
                               help="Commission Rules",
                               )
    no_discount_commission_percentage = fields.Float(string="No Discount Commission %",
                                                     help="Related Commission % when No discount", )
    max_discount_commission_percentage = fields.Float(string="Max Discount %", help="Maximum Discount %", )
    gt_discount_commission_percentage = fields.Float(string="Discount > 25% Commission %",
                                                     help="Related Commission % when discount '%' is greater than 25%", )
    standard_commission = fields.Float(string="Standard Commission percentage")

    @api.constrains('user_ids')
    def _check_uniqueness(self):
        '''This method checks constraint for only one commission group for each sales person'''
        for obj in self:
            ex_ids = self.search([('user_ids', 'in', [x.id for x in obj.user_ids])])
            if len(ex_ids) > 1:
                raise UserError('Only one commission type can be associated with each sales person!')
        return True

    # @api.constrains('affiliated_partner_ids','nonaffiliated_partner_ids')
    # def _check_partners(self):
    #     '''This method checks constraint for partner being either affiliated or non-affiliated, not both'''
    #     obj = self
    #     aff_partner = [x.id for x in obj.affiliated_partner_ids]
    #     nonaff_partner = [x.id for x in obj.nonaffiliated_partner_ids]
    #     common_partner = [x for x in aff_partner if x in nonaff_partner]
    #     if common_partner:
    #         raise Warning('Partner can either be affiliated or non-affiliated,not both!')
    #     return True

    # _constraints = [
    #     (_check_uniqueness, 'Only one commission type can be associated with each sales person!', ['user_ids']),
    #     (_check_partners, 'Partner can either be affiliated or non-affiliated,not both!', ['affiliated_partner_ids', 'nonaffiliated_partner_ids']),
    # ]


'''New class to handle sales commission exceptions'''


class SaleCommissionException(models.Model):
    _name = 'sale.commission.exception'
    _rec_name = 'commission_precentage'
    _description = 'Sale Commission Exception'

    based_on = fields.Selection([('Products', 'Products'),
                                 ('Product Categories', 'Product Categories'),
                                 ('Product Sub-Categories', 'Product Sub-Categories')], string="Based On",
                                help="commission exception based on", default='Products',
                                required=True)
    based_on_2 = fields.Selection([('Fix Price', 'Fix Price'),
                                   ('Margin', 'Margin'),
                                   ('Commission Exception', 'Commission Exception')], string="With",
                                  help="commission exception based on", default='Fix Price',
                                  required=True)
    commission_id = fields.Many2one('sale.commission', string='Sale Commission',
                                    help="Related Commission", )
    product_id = fields.Many2one('product.product', string='Product',
                                 help="Exception based on product", )
    categ_id = fields.Many2one('product.category', string='Product Category',
                               help="Exception based on product category")
    # order_category = fields.Integer(related='categ_id.parent_left', string='Order By', store=True)
    sub_categ_id = fields.Many2one('product.category', string='Product Sub-Category',
                                   help="Exception based on product sub-category")
    commission_precentage = fields.Float(string="Commission %")
    below_margin_commission = fields.Float(string="Below Margin Commission %")
    above_margin_commission = fields.Float(string="Above Margin Commission %")
    margin_percentage = fields.Float(string="Target Margin %")
    price = fields.Float(string="Target Price")
    price_percentage = fields.Float(string="Above price Commission %")

    category_store = fields.Many2many('product.category', string="Category store", compute="_compute_all_ids",
                                      store=True)

    @api.depends('based_on', 'sub_categ_id', 'categ_id')
    def _compute_all_ids(self):

        for line in self:
            category_lst = []
            if line.based_on == 'Product Categories':
                category_lst.append(line.categ_id.id)

                for child in line.categ_id.child_id:
                    if child.id not in category_lst:
                        category_lst.append(child.id)
                category_store = ''
                for num in category_lst:
                    category_store = category_store + ',' + str(num)
                line.category_store = category_lst
            elif line.based_on == 'Product Sub-Categories':

                for child in line.sub_categ_id.child_id:
                    if child.id not in category_lst:
                        category_lst.append(child.id)

                category_store = ''
                for num in category_lst:
                    category_store = category_store + ',' + str(num)

                line.category_store = category_lst

            else:
                line.category_store = category_lst


'''New class to handle discount based commission'''


class DiscountCommissionRules(models.Model):
    _name = 'discount.commission.rules'
    _rec_name = 'discount_percentage'
    _description = 'Discount Commission Rules'

    commission_id = fields.Many2one('sale.commission', string='Sale Commission',
                                    help="Related Commission", )
    discount_percentage = fields.Float(string="Discount %")
    commission_percentage = fields.Float(string="Commission %")
