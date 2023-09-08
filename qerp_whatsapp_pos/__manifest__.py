# -*- coding: utf-8 -*-
{
    'name': 'qerp_whatsapp_pos',
    'version': '13.0.1.0.0',
    'category': 'Base',
    'author': 'ERP Harbor Consulting Services',
    'summary': 'Generate QR Code for Sale',
    'website': 'http://www.erpharbor.com',
    'description': """""",
    'depends': [ 'point_of_sale',   'sale_management','tus_meta_wa_pos' ],
    'data': [
        # 'report/sale_order_report_template.xml',
        'views/pos_order_portal_template.xml',
        # 'views/qr_code_sale_view.xml',
    ],
    # "qweb" : [
    #     'static/src/xml/ClientDetailEdit.xml',
    # ],
    # 'assets': {
    #     'point_of_sale.assets': [
    #         'qerp_whatsapp_pos/static/src/js/ClientListScreen.js',
    #     ],
    # },
    #     'web.assets_qweb': [
    #         'qerp_whatsapp_pos/static/src/xml/**/*',
    #     ],
    #     # 'point_of_sale.assets': [
    #     #     'qerp_whatsapp_pos/static/src/xml/ClientDetailEdit.xml'
    #     # ],
    #     # 'web.assets_qweb': [
    #     #     'qerp_whatsapp_pos/static/src/xml/ClientDetailEdit.xml',
    #     # ],
    # },
    'installable': True,
}
