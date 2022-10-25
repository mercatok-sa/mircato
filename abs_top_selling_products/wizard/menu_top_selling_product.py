# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, fields, models,_
from datetime import datetime
from odoo.exceptions import ValidationError

### wizard
class TopSelling(models.TransientModel):
    _name = "topselling.orderline"
    _description = "Top Selling Product"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    state = fields.Selection([('price','Price'),('qty','Quantity')])    

    @api.onchange('date_to')
    def onchange_date_to(self):
        for record in self:
            if record.date_to < record.date_from:
                raise ValidationError("Please select right date")
            else:
                pass

    def top_selling_product(self):
        if self.state == 'price':
            sale_order_list = [] 
            line_list = []
            final_list = []
            order_line_list = []
            product_topselling = self.env['sale.products']
            sale_order_ids = self.env['sale.order'].search([('date_order','<=',self.date_to),('date_order','>=',self.date_from),('state','in',['sale','done'])])
            if sale_order_ids:
                for order in sale_order_ids:
                    sale_order_list.append(order)
                for order in sale_order_list:
                    for order_lines in order.order_line:
                        line_list.append(order_lines)
                for product in line_list:
                    total_amount = 0
                    for same_product in line_list:
                        if product.product_id == same_product.product_id:
                            total_amount = total_amount + same_product.price_subtotal
                    product_dict = { 'product' : product.product_id.id, 'amount' : total_amount }
                    topselling_product_id = product_topselling.create(product_dict)
                    if topselling_product_id.product not in final_list: 
                        order_line_list.append(topselling_product_id)
                        final_list.append(topselling_product_id.product)
            return {
            'name': _('Top Selling Products'),
            'type': 'ir.actions.act_window',
            'domain': [('id','in',[x.id for x in order_line_list])],
            'view_mode': 'tree',
            'res_id' : 'topselling_product_id',
            'res_model': 'sale.products',
            'view_id': False,
            'action' :'view_product_tree',
            'target' : 'current'
            }

        else: 
            sale_order_list = [] 
            line_list = []
            final_list = []
            order_line_list = []
            product_topselling = self.env['sale.quantity']
            sale_order_ids = self.env['sale.order'].search([('date_order','<=',self.date_to),('date_order','>=',self.date_from),('state','in',('sale','done'))])
            if sale_order_ids:
                for order in sale_order_ids:
                    sale_order_list.append(order)
                for order in sale_order_list:
                    for order_lines in order.order_line:
                        line_list.append(order_lines)
                for product in line_list:
                    total_amount = 0
                    for same_product in line_list:
                        if product.product_id == same_product.product_id:
                            total_amount = total_amount + same_product.product_uom_qty
                    product_dict = { 'product' : product.product_id.id, 'quantity' : total_amount }
                    topselling_product_id = product_topselling.create(product_dict)
                    if topselling_product_id.product not in final_list: 
                        order_line_list.append(topselling_product_id)
                        final_list.append(topselling_product_id.product)
            return {
            'name': _('Top Selling Products'),
            'type': 'ir.actions.act_window',
            'domain': [('id','in',[x.id for x in order_line_list])],
            'view_mode': 'tree',
            'res_id' : 'topselling_product_id',
            'res_model': 'sale.quantity',
            'view_id': False,
            'action' :'view_product_quantity_tree',
            'target' : 'current'
            }

