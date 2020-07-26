# -*- coding: utf-8 -*-
# (C)opyright Aadarsha Shrestha, 2019. See LICENSE for full copyright and licensing details.

{
    'name' : 'Trial Balance Accumulated',
    'version' : '1.0',
    'summary': 'Shows accumulated balance in Debit and Credit columns of Trial Balance',
    'sequence': 16,
    'category': 'Accounting',
    'description': """
Trial Balance Accumulated
=====================================
    """,
    'website': 'https://aadarsh.com.np',
    'images' : [],
    'depends' : ['account', 'account_financial_report_qweb'],
    'author': 'Aadarsha Shrestha',
    'company': 'Aadarsha Shrestha',
    'data': [
        'wizard/wizard_report_trial_view.xml',
        'views/report_trialbalance.xml',
        'wizard/trial_balance_wizard_view.xml',
        'report/report.xml',
        'views/trial_balance_adv.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
