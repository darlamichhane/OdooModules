{
    'name': 'AB Group: Global Auto Point',
    'version': '10.0.1',
    'summary': 'This app will handle all the enterprise activities of the AB Group of Company: Global Autopoint',
    'description': "This app will handle all the enterprise activities of the AB Group of Company: Global Autopoint",
    'category': 'Extra Tools',
    'author': 'DARSHAN LAMICHHANE',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/workorder.xml',
        'views/sale.xml',
        'views/vehicle.xml',
        'data/sequence.xml',
        'reports/report.xml',
        'reports/job_card.xml'
    ],
    'depends': ['base','mail','sale','hr','web_widget_timepicker','stock'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
