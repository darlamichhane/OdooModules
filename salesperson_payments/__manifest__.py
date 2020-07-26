# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Salesperson Payments',
    'version' : '10.0.1',
    'summary': 'This app helps you to create payments for more than one invoice at once.',
    'description': "Mass Payments based on Sales Person",
    'category': 'Accounting',
    'author': 'SAGAR JAYSWAL',
    'website': 'http://www.sagarcs.com',
    'license': 'AGPL-3',
    'data': ['wizard/mass_payments.xml',],
    'depends': ['base','account','sale'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
