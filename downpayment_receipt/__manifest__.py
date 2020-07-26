# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Advance receipt',
    'version': '10.0.1',
    'summary': 'This app helps to post better Accounting entries for stock.',
    'description': "This app helps to post better Accounting entries for stock",
    'category': 'Accounting',
    'author': 'Sagar Jayswal',
    'website': 'http://www.sagarcs.com',
    'license': 'AGPL-3',
    'data': [
        'views/invoice_report.xml',
        'views/account_invoice.xml'
    ],
    'depends': ['base', 'account','sale'],
    'installable': True,
    'application': False,
    'auto_install': False,

}
