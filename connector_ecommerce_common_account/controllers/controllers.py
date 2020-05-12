# -*- coding: utf-8 -*-
from odoo import http

# class ConnectorEcommerceCommonAccount(http.Controller):
#     @http.route('/connector_ecommerce_common_account/connector_ecommerce_common_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/connector_ecommerce_common_account/connector_ecommerce_common_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('connector_ecommerce_common_account.listing', {
#             'root': '/connector_ecommerce_common_account/connector_ecommerce_common_account',
#             'objects': http.request.env['connector_ecommerce_common_account.connector_ecommerce_common_account'].search([]),
#         })

#     @http.route('/connector_ecommerce_common_account/connector_ecommerce_common_account/objects/<model("connector_ecommerce_common_account.connector_ecommerce_common_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('connector_ecommerce_common_account.object', {
#             'object': obj
#         })