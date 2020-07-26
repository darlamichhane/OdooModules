# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'General Ledger Account Group',
    'version' : '10.0.1',
    'summary': 'This app helps to General Ledger .',
    'description': "General Ledger",
    'category': 'Accounting',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/general_ledger_view.xml',
        'views/general_ledger_pdf.xml',
        'views/general_ledger_report.xml',
        
    ],
    'depends': ['base', 'account'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
