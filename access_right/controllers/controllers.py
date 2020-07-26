# -*- coding: utf-8 -*-
from odoo import http

# class AccessRight(http.Controller):
#     @http.route('/access_right/access_right/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/access_right/access_right/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('access_right.listing', {
#             'root': '/access_right/access_right',
#             'objects': http.request.env['access_right.access_right'].search([]),
#         })

#     @http.route('/access_right/access_right/objects/<model("access_right.access_right"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('access_right.object', {
#             'object': obj
#         })