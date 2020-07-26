# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Service Charge',
    'version': '10.0.1',
    'summary': 'This app helps to add Service charge on Invoice.',
    'description': "Service Charge on Invoice",
    'category': 'Accounting',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/account_config_settings.xml',
        'views/account_invoice.xml',
        'views/sale_order.xml',
    ],
    'depends': ['base', 'account', 'sale',],
    'installable': True,
    'application': False,
    'auto_install': False,

}
