{
    'name': 'AB Group ERP',
    'version': '10.0.1',
    'summary': 'This app will handle all the enterprise activities of the AB Group of Company.',
    'description': "This app will handle all the enterprise activities of the AB Group of Company.",
    'category': 'Extra Tools',
    'author': 'DARSHAN LAMICHHANE',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'views/workorder.xml',
        'views/sale.xml',
        'views/vehicle.xml',
        'data/sequence.xml',
        'reports/report.xml',
        'reports/job_card.xml'
    ],
    'depends': ['base','mail','sale','web_widget_timepicker'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
