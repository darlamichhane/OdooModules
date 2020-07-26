# -*- coding: utf-8 -*-
##############################################################################
#
#    Change menu color
#    Copyright (C) 2016 July
#    1200 Web Development
#    http://1200wd.com/
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Pos Subtotal to quantity',
    'version': '10.0.1',
    'summary': 'This app helps to calculate quantity of product based on applied subtotal amount in Point of Sale UI for AB Petrolieum.',
    'description': "POS Subtotal to quantity",
    'category': 'POS',
    'author': 'Anil KC',
    'website': 'http://www.aspatalservices.com',
    'license': 'AGPL-3',
    'depends': ['point_of_sale'],
    'data': [
            'views/import.xml',
            'views/pos_config.xml',
        ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
