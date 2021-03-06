# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Doctor Tracker',
    'version' : '10.0.1',
    'summary': 'This app helps you to track the sales related to doctor.',
    'description': "Doctor Tracker",
    'category': 'Accounting',
    'author': 'SAGAR JAYSWAL',
    'website': 'http://www.sagarcs.com',
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'report/doc_rep.xml',
        'views/report_doctor.xml',
        'report/doctor_report_view.xml',
        'views/doctor_report_report.xml',
        
    ],
    'depends': ['base','account','sale'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
