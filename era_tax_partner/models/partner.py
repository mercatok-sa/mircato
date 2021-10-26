# -*- coding: utf-8 -*-
import qrcode
import base64
from io import BytesIO
from odoo import models, api, fields, _


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    tax_amount = fields.Float(string="Tax Amount", compute="_compute_tax_amount")


    @api.depends('tax_ids', 'price_unit','quantity')
    def _compute_tax_amount(self):
        for line in self:
            if line.tax_ids:
                line.tax_amount = line.price_total - line.price_subtotal
            else:
                line.tax_amount = 0.0


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    @api.onchange('partner_id')
    def _onchange_partner_warning_vat(self):
        if not self.partner_id:
            return
        partner = self.partner_id
        warning = {}
        if partner.company_type == 'company' and not partner.vat:
            title = ("Warning for %s") % partner.name
            message = _("Please add VAT ID for This Partner '%s' !") % (partner.name)
            warning = {
                'title': title,
                'message': message,
            }
        if warning:
            res = {'warning': warning}
            return res

    def get_qr_code_data(self):
        customer_name = ""
        customer_vat = ""
        if self.move_type in ('out_invoice', 'out_refund'):
            sellername = str(self.company_id.name)
            seller_vat_no = self.company_id.vat or ''
            if self.partner_id.company_type == 'company':
                customer_name = self.partner_id.name
                customer_vat = self.partner_id.vat
        else:
            sellername = str(self.partner_id.name)
            seller_vat_no = self.partner_id.vat
            customer_name = self.company_id.name
            customer_vat = self.company_id.vat
        currency_id = self.currency_id
        qr_code = " Seller Name: " + sellername
        qr_code += " Seller VAT NO.: " + seller_vat_no if seller_vat_no else " "
        qr_code += " | Date: " + str(self.invoice_date) if self.invoice_date else "| Date: " + str(self.create_date.date())
        qr_code += " | Total Tax: " + str(round(self.amount_tax, 2)) + str(currency_id.symbol)
        qr_code += " | Total Amount: " + str(round(self.amount_total, 2)) + str(currency_id.symbol)
        if customer_name:
            qr_code += " | Customer Name: " + customer_name
        if customer_vat:
            qr_code += " | Customer Vat: " + customer_vat
        # print(qr_code)
        return qr_code

    qr_code = fields.Binary(string="QR Code", attachment=True, store=True)

    @api.onchange('invoice_line_ids.product_id')
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_qr_code_data())
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_warning_vat(self):
        if not self.partner_id:
            return
        partner = self.partner_id
        warning = {}
        if partner.company_type == 'company' and not partner.vat:
            title = ("Warning for %s") % partner.name
            message = _("Please add VAT ID for This Partner '%s' !") % (partner.name)
            warning = {
                'title': title,
                'message': message,
            }
        if warning:
            res = {'warning': warning}
            return res


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _onchange_partner_warning_vat(self):
        if not self.partner_id:
            return
        partner = self.partner_id
        warning = {}
        if partner.company_type == 'company' and not partner.vat:
            title = ("Warning for %s") % partner.name
            message = _("Please add VAT ID for This Partner '%s' !") % (partner.name)
            warning = {
                'title': title,
                'message': message,
            }
        if warning:
            res = {'warning': warning}
            return res
