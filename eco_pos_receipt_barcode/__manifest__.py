# -*- coding: utf-8 -*-
{
    'name': 'ECO:POS  Receipt Barcode',
    'version': '17.0',
    'summary': """Pos Custom Receipt change odoo POS receipt""",
    'author': "ECo-Tech",
    'category': 'Point Of Sale',
    'depends': ['point_of_sale'],

    'assets': {
        'point_of_sale._assets_pos': [
            'eco_pos_receipt_barcode/static/src/lib/JsBarcode.all.min.js',
            'eco_pos_receipt_barcode/static/src/js/**/*',
            'eco_pos_receipt_barcode/static/src/xml/**/*'
        ],
    },

}
