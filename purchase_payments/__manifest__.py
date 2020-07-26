# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Purchase TDS Payment',
    'version' : '10.0.1',
    'summary': 'This app helps you to keep track of tds in purchasde payment',
    'description': "Mass Payments based on Sales Person",
    'category': 'Accounting',
    'author': 'SAGAR JAYSWAL',
    'website': 'http://www.sagarcs.com',
    'license': 'AGPL-3',
    'data': ['view/purchase_payments.xml',
    'view/reg_pay.xml'],
    'depends': ['base','account','sale','purchase'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
