# -*- coding: utf-8 -*-
{
    'name': 'IRD Synchronization',
    'version': '1.0.0',
    'category': 'Sale',
    'summary': '''
        This module Populates Materialized view as per the IRD anusuchi 5.
        ''',
    'author': 'Anil KC',
    'license': "OPL-1",
    'depends': [
        'sale'
    ],
    'data': [
        'views/ird_sync.xml'
    ],
    'demo': [],  
    'images': [],
    'auto_install': False,
    'installable': True,
    'application': True
}