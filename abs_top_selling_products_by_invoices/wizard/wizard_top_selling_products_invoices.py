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
from datetime import datetime
from odoo.exceptions import ValidationError

### Create new class for displaying table for top selling products with amount in from_date to to_date using wizard 
class TopSellingInvoices(models.TransientModel):
    _name = "topselling.invoices"
    _description = "Top Selling Invoices"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')

    @api.onchange('date_to')
    def onchange_date_to(self):
        for record in self:
            if record.date_to < record.date_from:
                raise ValidationError("Please select right date")
            else:
                pass

    ###Function for display tree view of products with amount in descending order for only customer invoices
    def top_selling_product(self):
        customer_invoice_list = [] 
        invoice_line_list = []
        final_list = []
        order_line_list = []
        product_topselling_customer_invoices = self.env['products.customerinvoices']
        customer_invoices_ids = self.env['account.move'].search([('invoice_date','<=',self.date_to),('invoice_date','>=',self.date_from),('state','in',['posted'])])
        if customer_invoices_ids:
            for customer_invoice in customer_invoices_ids:
                customer_invoice_list.append(customer_invoice)
            for customer_invoice in customer_invoice_list:
                for invoice_lines in customer_invoice.invoice_line_ids:
                    if invoice_lines.move_id.move_type == 'out_invoice':
                        invoice_line_list.append(invoice_lines)
            for product in invoice_line_list:
                if product.product_id:
                    total_amount = 0
                    for same_product in invoice_line_list:
                        if product.product_id == same_product.product_id:
                            total_amount = total_amount + same_product.price_subtotal
                    product_dict = { 'product' : product.product_id.id, 'amount' : total_amount }
                    topselling_product_id = product_topselling_customer_invoices.create(product_dict)
                    if topselling_product_id.product not in final_list and topselling_product_id.product.name != 'Down payment': 
                        order_line_list.append(topselling_product_id)
                        final_list.append(topselling_product_id.product)
        return {
            'name': _('Top Selling Products'),
            'type': 'ir.actions.act_window',
            'domain': [('id','in',[x.id for x in order_line_list])],
            'view_mode': 'tree',
            'res_model': 'products.customerinvoices',
            'view_id': False,
            'action' :'view_top_selling_product_tree',
            'target' : 'current'
        }
