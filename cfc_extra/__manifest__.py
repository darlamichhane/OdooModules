# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'CFC Extra',
    'version' : '10.0.1',
    'summary': 'This app helps to add features acccording to cfc .',
    'description': "CFC Extra addons",
    'category': 'Stock',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/cfc_inventory.xml',
        'views/cfc_account.xml',
        'views/cfc_product.xml',
        'views/cfc_purchase.xml',
        'views/cfc_sale.xml',
        'wizards/account_invoice_reprint.xml',
        
    ],
    'depends': ['base', 'stock', 'purchase', 'account'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
