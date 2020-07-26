{
    'name': 'AB Access Control',
    'version': '10.0.1',
    'summary': 'This app will handle access right of ERP User.',
    'description': "This app will handle access right of ERP User.'",
    'category': 'Extra Tools',
    'author': 'DARSHAN LAMICHHANE',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/view.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/account_invoice.xml'
    ],
    'depends': ['base','sale','account','purchase','stock','point_of_sale'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
