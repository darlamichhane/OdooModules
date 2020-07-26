{
    'name': 'Swastika Access Control',
    'version': '10.0.1',
    'summary': 'This app will handle access right of non-admin user.',
    'description': "This app will handle access right of non-admin user.'",
    'category': 'Extra Tools',
    'author': 'DARSHAN LAMICHHANE',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/view.xml',
        'views/sale_order.xml',
        'views/account_invoice.xml'
    ],
    'depends': ['base','sale','account'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
