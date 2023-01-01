# -*- coding: utf-8 -*-

{
    "name": "e-Invoice KSA POS | Receipt | QR code pos | tax invoice | report | qrcode | ZATCA | vat  | electronic | einvoice | e-invoice sa "
            "| accounting | tax  | Zakat, Tax and Customs Authority | point of sale  | order receipt | qrcode pos | invoicing | stock | free",
    "version": "1.0",
    'depends': ['base', 'point_of_sale'],
    "author": "Genius Valley",
    "category": "Point of Sale",
    "website": "https://genius-valley.com/",
    "support": "odoo@gvitt.com",
    "images": ["static/description/assets/main_screenshot.gif"],
    "price": "0",
    "license": "OPL-1",
    "currency": "USD",
    "summary": "e-Invoice KSA POS | Receipt | QR code pos| tax invoice | report | qrcode | ZATCA | vat  | electronic | einvoice | e-invoice sa "
            "| accounting | tax  | Zakat, Tax and Customs Authority | point of sale  | order receipt |qrcode pos | free | الفاتورة الضريبية | الفوترة  "
               "  هيئة الزكاة والضريبة والجمارك | الالكترونية | ",
    "description": """
    e-Invoice in Kingdom of Saudi Arabia
    and prepare tax invoice to be ready for the second phase.
    Zakat, Tax and Customs Authority
    الفوترة الإلكترونية - الفاتورة الضريبية - المملكة العربية السعودية
    المرحلة الاولي -  مرحلة الاصدار 
    هيئة الزكاة والضريبة والجمارك

 Versions History --------------------

* version 1.0: 6-OCT-2021
    - initial version contain order receipt with QR code
    
    """
    ,
    "data": [
        "view/assets.xml"
    ],
    "qweb": [
        "static/src/xml/pos_receipt.xml"
    ],
    "installable": True,
    "auto_install": True,
    "application": True,
}
