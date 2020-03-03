# -*- coding: utf-8 -*-
from odoo import http

# class BaseEcommerceClient(http.Controller):
#     @http.route('/base_ecommerce_client/base_ecommerce_client/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_ecommerce_client/base_ecommerce_client/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_ecommerce_client.listing', {
#             'root': '/base_ecommerce_client/base_ecommerce_client',
#             'objects': http.request.env['base_ecommerce_client.base_ecommerce_client'].search([]),
#         })

#     @http.route('/base_ecommerce_client/base_ecommerce_client/objects/<model("base_ecommerce_client.base_ecommerce_client"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_ecommerce_client.object', {
#             'object': obj
#         })