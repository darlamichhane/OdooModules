# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Requisition Form',
    'version' : '10.0.1',
    'summary': 'This app helps to make requisition before issuing.',
    'description': "Requisition form",
    'category': 'Stock',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/requisition_view.xml',
        'views/stock_picking_view.xml',
        'data/sequence.xml',
        'report/report_requisition.xml',
        'report/requisition_pdf.xml',

    ],
    'depends': ['base', 'account', 'stock','ab_global_autopoint'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
