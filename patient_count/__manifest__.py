# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Patient Count',
    'version' : '10.0.1',
    'summary': 'This app helps you to get the doctorwise patient count .',
    'description': "Patient Count Report",
    'category': 'Accounting',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/doctor_count_report.xml'
        
    ],
    'depends': ['base', 'account'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
