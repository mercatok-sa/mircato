{
    "name": "POS Shop Analytic Account",
    "summary": """Configure & Pass Analytic account for Sales & Invoices in POS""",
    "description": """
        This module helps to configure an Analytic account for each POS shop in Odoo.
        By selecting an analytic account, it will be passed to the account entries and Invoice created from POS.
    """,
    "author": "Sanesquare Technologies",
    "website": "https://www.sanesquare.com/",
    "support": "odoo@sanesquare.com",
    "license": "OPL-1",
    "category": "Sales/Point of Sale",
    "version": "15.0.1.0.1",
    "depends": ["point_of_sale"],
    "images": ["static/description/pos_shop_analytic_account_v15.png"],
    "data": [
        "views/pos_config_view.xml",
    ],
}
