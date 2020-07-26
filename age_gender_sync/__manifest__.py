# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Age and Sex Sync',
    'version' : '10.0.1',
    'summary': 'This app helps to add age and sex to the customer attributes.',
    'description': "Age and Sex Synchronization",
    'category': 'Extra',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/res_partner.xml',
        
    ],
    'depends': ['base', 'bahmni_atom_feed'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
