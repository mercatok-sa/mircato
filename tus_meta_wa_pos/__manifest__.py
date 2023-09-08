{
    'name': 'Odoo Meta WhatsApp POS',
    'version': '1.0.',
    'author': 'TechUltra Solutions',
    'category': 'Point of Sale',
    'live_test_url': 'https://www.techultrasolutions.com/blog/news-2/odoo-whatsapp-integration-a-boon-for-business-communication-25',
    'website': 'www.techultrasolutions.com',
    'price': 19,
    'currency': 'USD',
    'description': """

    """,
    'depends': ['tus_meta_whatsapp_base','point_of_sale'],
    'data': [
        'security/pos_security.xml',
        'data/wa_template.xml',
        'views/pos_config.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_frontend': [
        ],
        'point_of_sale.assets': [
            '/tus_meta_wa_pos/static/src/js/components/popup/pos_wa_composer.js',
            '/tus_meta_wa_pos/static/src/js/components/ReceiptScreen/ReceiptScreen.js',
            '/tus_meta_wa_pos/static/src/css/pos_ext.css',
        ],
        'web.assets_qweb': [
            '/tus_meta_wa_pos/static/src/js/components/popup/pos_wa_composer.xml',
            '/tus_meta_wa_pos/static/src/js/components/ReceiptScreen/ReceiptScreen.xml',
            '/tus_meta_wa_pos/static/src/js/components/ClientDetailsEdit.xml',
            '/tus_meta_wa_pos/static/src/js/components/ClientListScreen.xml',
            '/tus_meta_wa_pos/static/src/js/components/ClientLine.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images':['static/description/banner.jpg'],
    'summary': 'Whatsapp POS point of sale modules allows to send the receipt by whatsapp',
    'description': """
        whatsapp all in one and whatsapp pos will allow user to send the orders of point of sale to customer and customer can rate that.
    """,
    # 'post_init_hook': '_set_image_in_company',
}
