{
    'name': 'Stock Internal Transfers Accounts',
    "author": 'Zero Systems',
    "company": 'Zero for Information Systems',
    "website": "https://www.erpzero.com",
    "email": "sales@erpzero.com",
    'live_test_url': 'https://www.youtube.com/watch?v=JGs5HWoOZHo',
    'version': '1.0.2',
    'category': 'Warehouse',
    'summary': 'Stock journal Between Different locations',
    "description": """
    This system allows the creation of an accounting entry between the 
    different storage sites and according to the desire,
     support multi company,
     support community and enterprise
     You can allocate an inventory valuation account for each storage location separately,
     You can allocate an inventory Stock Journal for each storage location separately,
     Intermediary account used when moving stock from a storage Location to another different storage Location,
     Intermediary account used when moving stock from a warehouse location to another different warehouse location,
     Intermediary account used when moving stock from a store location to another different store location,

    """,
    "sequence": 0,
    'depends': ['base','account','stock_account'],
    'data': [
        'views/view.xml',
    ],
    'license': 'OPL-1',
    'images': ['static/description/logo.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 65.0,
    'currency': 'USD',
    "pre_init_hook": "pre_init_check",
}

