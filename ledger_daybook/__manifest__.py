# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'General Ledger Day Book',
    'version' : '10.0.1',
    'summary': 'This app helps to General Ledger .',
    'description': "General Ledger",
    'category': 'Accounting',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/ledger_daybook_view.xml',
        'views/ledger_daybook_pdf.xml',
        'views/ledger_daybook_report.xml',
        
    ],
    'depends': ['base', 'account'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
