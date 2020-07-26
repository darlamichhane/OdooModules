# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Stock Consumption Report',
    'version' : '10.0.1',
    'summary': 'This app helps to print Stock Consumption Report .',
    'description': "Stock Consumption Report",
    'category': 'Stock',
    'author': 'Anil',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/consumption_view.xml',
        'views/consumption_pdf.xml',
        'views/consumption_report.xml',
        'views/consumption_pdf_view.xml',
        
    ],
    'depends': ['base', 'account'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
