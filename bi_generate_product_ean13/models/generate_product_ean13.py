# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api
from datetime import datetime
import random
# import barcode

try:
    from barcode.writer import ImageWriter
except ImportError:
    ImageWriter = None  # lint:ok
import base64
import os


class BiProductGenerateBarcodeManually(models.TransientModel):
    _name = 'bi.product.generate.barcode.manually'

    generate_type = fields.Selection([('date', 'Generate Barcode EAN13 (Using Today Date)'),
                                      ('random', 'Generate Barcode EAN13 (Using Random Number)')],
                                     string='Barcode Generate Option', default='date')

    def generate_barcode_manually(self):
        for record in self.env['product.product'].browse(self._context.get('active_id')):
            if self.generate_type == 'date':
                bcode = self.env['barcode.nomenclature'].sanitize_ean(
                    "%s%s" % (record.id, datetime.now().strftime("%d%m%y%H%M")))
            else:
                number_random = int("%0.13d" % random.randint(0, 999999999999))
                bcode = self.env['barcode.nomenclature'].sanitize_ean("%s" % (number_random))
            record.write({'barcode': bcode})

        return True


class BiGenerateProductBarcode(models.TransientModel):
    _name = 'bi.product.generate.barcode'

    overwrite = fields.Boolean(String="Overwrite Exists Ean13")
    generate_type = fields.Selection([('date', 'Generate Barcode EAN13 (Using Today Date)'),
                                      ('random', 'Generate Barcode EAN13 (Using Random Number)')],
                                     string='Barcode Generate Option', default='date')

    def generate_barcode(self):
        for record in self.env['product.product'].browse(self._context.get('active_ids')):
            if not self.overwrite and record.barcode:
                continue

            if self.generate_type == 'date':
                bcode = self.env['barcode.nomenclature'].sanitize_ean(
                    "%s%s" % (record.id, datetime.now().strftime("%d%m%y%H%M")))
            else:
                number_random = int("%0.13d" % random.randint(0, 999999999999))
                bcode = self.env['barcode.nomenclature'].sanitize_ean("%s" % (number_random))

            record.write({'barcode': bcode,

                          })
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
