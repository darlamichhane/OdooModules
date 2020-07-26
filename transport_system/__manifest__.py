# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Transport Management System',
    'version' : '10.0.1',
    'summary': 'This app helps to generate Tax Invoice as per IRD clause.',
    'description': "Tax Invoice",
    'category': 'Accounting',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/transport_menus.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/account_invoice.xml',
        'views/custom_office.xml',
        'views/transport_manifest.xml',
        'views/transit.xml',
        'report/tax_invoice_menu.xml',
        'report/tax_invoice_template.xml',
        'report/manifest_pdf.xml',
        'report/report_manifest.xml',
        'wizards/transit_manifest.xml',

    ],
    'depends': ['base', 'account', 'sale', 'vehicle_info', 'hierarchical_address_nepal'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
