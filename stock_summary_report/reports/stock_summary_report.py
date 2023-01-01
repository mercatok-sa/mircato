# -*- coding: utf-8 -*-

from odoo import models, fields, _
import datetime
from datetime import datetime, timedelta, date
import dateutil.parser
import pytz

class StockSummaryReportXls(models.AbstractModel):
    _name = 'report.stock_summary_report.stock_summary_report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('Stock Summary')
        
        self.print_header(data, workbook,sheet)
        self.get_product_with_category(data,workbook,sheet)

    def print_header(self,data, workbook, sheet):
        format_header = workbook.add_format({'font_name': 'Arial','font_size': 10, 'align': 'center', 'bold': True,'bg_color': 'silver'})
        format_header_no_bg = workbook.add_format({'font_name': 'Arial','font_size': 10, 'align': 'center', 'bold': True})
        format_header_title = workbook.add_format({'font_name': 'Arial','font_size': 12, 'align': 'center', 'bold': True})
        company = self.env['res.company'].search([('id','=',data['form']['company_id'])])
        user = self.env.user.name
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.timezone("Asia/Kathmandu")
        time = pytz.utc.localize(datetime.now()).astimezone(tz)
        sheet.merge_range('A1:F1', 'Generated On : ' + str(time.strftime("%d/%m/%Y, %I:%M:%S %p"))+ "\t \t \t By:  " + str(user), format_header_no_bg)
        sheet.merge_range('A2:F2', company.name, format_header_title)

        sheet.merge_range('A4:F4', 'Location: '+ str(data['location']), format_header_no_bg)
        
        sheet.merge_range('A5:F5', 'Stock Summary', format_header_title)

        # sheet.merge_range('A6:N6', 'Date: ' + date, format_header_no_bg)
        sheet.write('C6', 'From', format_header_no_bg)
        sheet.write('C7',  data['form']['start_date'], format_header_no_bg)
        sheet.write('F6', 'TO', format_header_no_bg)
        sheet.write('F7',  data['form']['end_date'], format_header_no_bg)
        sheet.write('A8', 'Particulars', format_header)
        sheet.write('B8', 'UOM', format_header)
        sheet.write('C8', 'Opening Balance', format_header)
        sheet.write('D8', 'Inwards', format_header)
        sheet.write('E8', 'Outwards', format_header)
        sheet.write('F8', 'Closing Balance', format_header)
        

    def get_records(self,data, location=None,product_id=None):
        '''
        @param start_date: start date
        @param end_date: end date
        @param location_id: location ID
        @param product_id: Product IDs
        @returns: recordset
        '''
        domains = []
        domains += [
            ('date', '>=', data['form']['start_date']),
            ('date', '<=', data['form']['end_date']),
            ('state', '=', 'done'),
            ('product_id.id', '=', product_id),
            '|',
            ('location_id.id', '=', location),
            ('location_dest_id.id', '=', location)
        ]
        records = self.env['stock.move.line'].search(domains, order='date asc')
        product_id = self.env['product.product'].search([('id','=',product_id),('type','=','product')])
        location_name = self.env['stock.location'].search([('id','=',location)]).display_name
        opening_date = datetime.strptime(data['form']['start_date'], "%Y-%m-%d").date() + timedelta(days=-1)
        closing_date = datetime.strptime(data['form']['end_date'], "%Y-%m-%d").date()
        opening = product_id.with_context({'to_date': str(opening_date),'location': location}).qty_available
        opening_value = product_id.with_context({'to_date': str(opening_date),'location': location}).stock_value
        closing = product_id.with_context({'to_date': str(closing_date),'location': location}).qty_available
        closing_value = product_id.with_context({'to_date': str(closing_date),'location': location}).stock_value
        total_in = 0
        total_in_value =0
        for record in (records.filtered(lambda r: r.location_dest_id.id == location)):
            total_in += record.product_uom_id._compute_quantity(record.qty_done, record.product_id.uom_id)
            total_in_value += record.qty_done
        total_out = 0 
        total_out_value = 0
        for record in (records.filtered(lambda r: r.location_id.id == location)):
            total_out += record.product_uom_id._compute_quantity(record.qty_done, record.product_id.uom_id)
            total_out_value += record.qty_done
        summary = {
                    'product' : product_id,
                    'product_name': product_id.name,
                    'product_uom' : product_id.uom_id.name,
                    'opening': opening,
                    'closing': closing,
                    'total_in' :total_in,
                    'total_out' : total_out,
                    }
        return summary
    def get_product_with_category(self,data,workbook,sheet):
        # format of Cells according to data type and categories
        format_total_string = workbook.add_format({'font_name': 'Arial','font_size': 10, 'align': 'center', 'bold': True,'bg_color': 'silver'})
        format_string = workbook.add_format({'font_name': 'Arial','font_size': 10, 'align': 'left','bold': False})
        format_numeric = workbook.add_format({'font_name': 'Arial','font_size': 10, 'num_format': '#,##0.00','bold': False})
        
        category_name_format = workbook.add_format({'font_name': 'Arial','font_size': 10, 'align': 'left','bold': True, 'bg_color': 'silver'})
        category_format_numeric = workbook.add_format({'font_name': 'Arial','font_size': 10, 'num_format': '#,##0.00','bold': True, 'bg_color': 'silver'})
        #
        location = data['form']['location_id']
        products = self.env['product.product'].search([('type','=','product'),('location_id.id', '=', data['form']['location_id'])])
        categories = list(set([product.categ_id.id for product in products]))
        categ_records = self.env['product.category'].search([('id', 'in', categories)])
        row = category_row = 8
        for category in categ_records:
            category_opening = category_in = category_out = category_closing =0
            sheet.write(category_row, 0, category.name, category_name_format)
            row = category_row +1
            cate_products = self.env['product.product'].search([('categ_id.id','=',category.id),('type','=','product'),('location_id.id', '=', data['form']['location_id'])])
            for product in cate_products:
                summary = self.get_records(data, location= data['form']['location_id'], product_id = product.id)
                sheet.write(row, 0, summary['product_name'], format_string)
                sheet.write(row, 1, summary['product_uom'], format_string)
                sheet.write(row, 2, summary['opening'], format_numeric)
                
                sheet.write(row, 3, summary['total_in'], format_numeric)
                
                sheet.write(row, 4, summary['total_out'], format_numeric)
                
                sheet.write(row, 5, summary['closing'], format_numeric)
            category_row = row +1 