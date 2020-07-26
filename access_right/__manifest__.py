# -*- coding: utf-8 -*-
{
    'name': "Access-rights",

    'summary': """
        Access rights for SayaPatri Tech""",

    'description': """
       This module is for maintaing access rights within Aspatal Services V1 which is managed and operated by 
       SayaPatri Technology Pvt,Ltd , Kathmandu ,Nepal
    """,

    'author': "Abhick Dahal",
    'website': "aspatalservices.com.np",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Access Rights',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'sales_team','purchase','stock','bahmni_stock','procurement'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
