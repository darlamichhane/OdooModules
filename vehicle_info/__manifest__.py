# -*- coding: utf-8 -*-
{
    'name': "Vehicle Information",
    'version': 'TIMS-1.0',
    'summary': """Manage Transport Vehicle Management""",
    'description': """This Module Manage Transport Vehicle Management""",
    'author': "Utshav Ghimire",
    'company': 'Sayapatri Technology',
    'website': "https://www.sayapatritech.com",
    'category': 'Warehouse',
    'depends': ['base', 'sale','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/vehicle_information.xml',
        'views/hr_employee.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
