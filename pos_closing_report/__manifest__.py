{
    'name': "Sale Details Report",
    'summary': """""",
    'description': """""",
    'author': 'Eco-Tech, Omnya Rashwan',
    'category': 'Products',
    'version': '16.0.1.1',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'reports/report_sale_details.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_closing_report/static/src/js/SalesDetailsReport.js',
            'pos_closing_report/static/src/xml/SaleDetailsReport.xml',
        ],
    },

    'installable': True,
}
