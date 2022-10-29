# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2022-today Ascetic Business Solution <www.asceticbs.com>
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
from odoo.exceptions import ValidationError

# create new class TopProductCategoryWizard. 
class TopProductCategoryWizard(models.TransientModel):
    _name = "top.product.category.wizard"
    _description = 'Top Product Category Wizard'

    from_date = fields.Date("From date")  
    to_date = fields.Date(string="To date")

    #create function for top selling product.
    def top_product_category(self):
        new_product_category_list = []
        final_product_category_list = []    
        product_category_list = []
        top_product_category_object = self.env['top.product.category']
        category_ids = self.env['product.category'].search([]) 
        if category_ids:
            for category_id in category_ids:
                count = 0                             
                if category_id.id and self.from_date and self.to_date:
                    if self.from_date < self.to_date:
                        order_ids = self.env['sale.order'].search([('date_order','>=',self.from_date),('date_order','<=',self.to_date),('state', 'in', ['sale','done'])])
                        if order_ids: 
                            for order_id in order_ids:
                                if order_id:
                                    for line_id in order_id.order_line:
                                        if line_id: 
                                            for product in line_id.product_id:
                                                if product:  
                                                    if  product.categ_id.id == category_id.id:   
                                                        count = count + line_id.price_subtotal 
                            product_category_dict = {'product_category_id':category_id.id,'amount':count}
                            new_line = top_product_category_object.create(product_category_dict) 
                            product_category_list.append(new_line) 
                            for product_category in product_category_list:
                                if product_category.product_category_id not in new_product_category_list:
                                    final_product_category_list.append(product_category)
                                    new_product_category_list.append(product_category.product_category_id)
                    else:
                        raise ValidationError("Invalid date period")     
        return {
            'name': _('Top Selling Product Category'),
            'type': 'ir.actions.act_window',
            'domain':[('id','in',[x.id for x in final_product_category_list])],   
            'view_mode': 'tree',
            'res_model': 'top.product.category',
            'action':'view_top_product_category',
            'view_id': False,
            'target': 'current',
            }
