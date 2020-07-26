# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Department Purchase Report',
    'version' : '10.0.1',
    'summary': 'This app helps you to get the purchase report of Department group by department name .',
    'description': "Department Purchase Report",
    'category': 'Accounting',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/department_expense_view.xml',
        'views/department_expense_report.xml',
        'views/department_expense_pdf.xml'
        
    ],
    'depends': ['base', 'account'],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
