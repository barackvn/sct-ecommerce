# -*- coding: utf-8 -*-
from odoo import http

# class BaseApiClient(http.Controller):
#     @http.route('/base_api_client/base_api_client/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_api_client/base_api_client/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_api_client.listing', {
#             'root': '/base_api_client/base_api_client',
#             'objects': http.request.env['base_api_client.base_api_client'].search([]),
#         })

#     @http.route('/base_api_client/base_api_client/objects/<model("base_api_client.base_api_client"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_api_client.object', {
#             'object': obj
#         })