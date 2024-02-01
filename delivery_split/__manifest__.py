# -*- coding: utf-8 -*-
{
    'name': 'Delivery split',
    'version': '16.0.1.0.0',
    'summary': 'This Module allows users to make multiple delivery based on delivery date in sale order line',
    'description': """This Module allows users to make multiple delivery based on delivery date in sale order line""",
    'license': 'OPL-1',
    'author': 'odoo',
    'website': 'https://www.odoo.com',
    'category': 'sale',
    'depends': ['sale_management', 'stock'],
    'data': [
        'views/sale_order.xml',
    ],
}
