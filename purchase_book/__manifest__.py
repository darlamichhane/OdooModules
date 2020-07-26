# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Purchase Book Report',
    'version' : '10.0.1',
    'summary': 'This app helps you to get the purchase excel report .',
    'description': "Purchase Book Report",
    'category': 'Accounting',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'wizard/purchase_book.xml'
        
    ],
    'depends': ['base', 'account'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
