# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Salesperson Income Report',
    'version' : '10.0.1',
    'summary': 'This app helps you to get the income report of Salesperson .',
    'description': "Salesperson wise Income Report ",
    'category': 'Accounting',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/salesperson_qweb_view.xml',
        'views/salesperson_qweb_report.xml',
        'views/salesperson_qweb_pdf.xml'
        
    ],
    'depends': ['base', 'account'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
