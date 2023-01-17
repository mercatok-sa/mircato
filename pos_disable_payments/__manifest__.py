# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    "name": "Allow/Disable POS Features Point of Sales Access rights POS Restrict User staff permissions",
    "version": "15.0.0.7",
    "category": "Point of Sale",
    'summary': 'POS hide Features POS Access rights pos Disable Payment disable Qty pos Discount pos disable price pos restric pos Limitations pos Disable pos enabled POS deny pos hide features pos permissions pos user pos extra',
    "description": """

	Purpose :-
	Allow/Deny POS Features like Payment Qty Discount Edit Price, Remove Orderline for Particular POS User...!!!
	odoo point of sales disable payment option on POS 
	odoo point of sales disable Discount option on POS
	odoo point of sales disable Edit Price option on POS
	odoo point of sales disable change Price option on POS
	odoo point of sales disable Remove Orderline option on POS
	odoo point of sales disable delete Orderline option on POS
	odoo point of sales disable Remove Order line option on POS
	odoo point of sales disable delete Order line option on POS

	odoo point of sale disable payment option on point of sales 
	odoo point of sale disable Discount option on point of sales
	odoo point of sale disable Edit Price option on point of sales
	odoo point of sale disable change Price option on point of sales
	odoo point of sale disable Remove Orderline option on point of sales
	odoo point of sale disable delete Orderline option on point of sales
	odoo point of sale disable Remove Order line option on point of sales
	odoo point of sale disable delete Order line option on point of sales

	odoo POS disable payment option POS 
	odoo POS disable Discount option POS
	odoo POS disable Edit Price option POS
	odoo POS disable change Price option POS
	odoo POS disable Remove Orderline option POS
	odoo POS disable delete Orderline option POS
	odoo POS disable Remove Order line option POS
	odoo POS disable delete Order line option POS

	odoo point of sale apply and disable payment option point of sale 
	odoo point of sale apply and disable Discount option point of sale
	odoo point of sale apply and disable Edit Price option point of sale
	odoo point of sale apply and disable change Price option point of sale
	odoo point of sale apply and disable Remove Orderline option point of sale
	odoo point of sale apply and disable delete Orderline option point of sale
	odoo point of sale apply and disable Remove Order line option point of sale
	odoo point of sale apply and disable delete Order line option point of sale


	odoo point of sales restrict payment option on POS 
	odoo point of sales restrict Discount option on POS
	odoo point of sales restrict Edit Price option on POS
	odoo point of sales restrict change Price option on POS
	odoo point of sales restrict Remove Orderline option on POS
	odoo point of sales restrict delete Orderline option on POS
	odoo point of sales restrict Remove Order line option on POS
	odoo point of sales restrict delete Order line option on POS

	odoo point of sale restrict payment option on point of sales 
	odoo point of sale restrict Discount option on point of sales
	odoo point of sale restrict Edit Price option on point of sales
	odoo point of sale restrict change Price option on point of sales
	odoo point of sale restrict Remove Orderline option on point of sales
	odoo point of sale restrict delete Orderline option on point of sales
	odoo point of sale restrict Remove Order line option on point of sales
	odoo point of sale restrict delete Order line option on point of sales

	odoo POS restrict payment option POS 
	odoo POS restrict Discount option POS
	odoo POS restrict Edit Price option POS
	odoo POS restrict change Price option POS
	odoo POS restrict Remove Orderline option POS
	odoo POS restrict delete Orderline option POS
	odoo POS restrict Remove Order line option POS
	odoo POS restrict delete Order line option POS

	odoo point of sale apply and restrict payment option point of sale 
	odoo point of sale apply and restrict Discount option point of sale
	odoo point of sale apply and restrict Edit Price option point of sale
	odoo point of sale apply and restrict change Price option point of sale
	odoo point of sale apply and restrict Remove Orderline option point of sale
	odoo point of sale apply and restrict delete Orderline option point of sale
	odoo point of sale apply and restrict Remove Order line option point of sale
	odoo point of sale apply and restrict delete Order line option point of sale
	""",
    "author": "BrowseInfo",
    "website": "https://www.browseinfo.in",
    "price": 20,
    "currency": 'EUR',
    "depends": ['base', 'point_of_sale', 'pos_hr','pos_discount'],
    "data": [
        'views/custom_pos_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_disable_payments/static/src/js/CustomNumpadWidget.js',
            'pos_disable_payments/static/src/js/ProductScreen.js',
            'pos_disable_payments/static/src/js/models.js',
        ],
        'web.assets_qweb': [
            'pos_disable_payments/static/src/xml/**/*',
        ],
    },
    "auto_install": False,
    "installable": True,
    'live_test_url': 'https://youtu.be/p_Xuz95CAgg',
    "images": ['static/description/Banner.png'],
    'license': 'OPL-1',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
