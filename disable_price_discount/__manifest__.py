# This is for disable the (Price,Discount,+/-) Button in POS Refund Order.
{
    'name': 'Disable Price and Discount',
    'version': '15.0',
    'category': 'Point of Sale',
    'summary': 'Disable Price and Discount for Refund in POS ',
    'author': 'Akili Systems PVT. LTD.',
    'company': 'Akili Systems PVT. LTD.',
    'maintainer': 'Akili Systems PVT. LTD.',
    'images': ['static/description/icon.png'],
    'website': 'https://akilisystems.in',
    'depends': ['point_of_sale','web'],
    'data': [ ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'assets': {
        'point_of_sale.assets': [
            'disable_price_discount/static/src/js/models.js',
        ],
        'web.assets_qweb': [
            'disable_price_discount/static/src/xml/pos_return.xml',
        ],
    },
}


