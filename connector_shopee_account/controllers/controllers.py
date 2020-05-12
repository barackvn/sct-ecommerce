# -*- coding: utf-8 -*-
from odoo import http

# class ConnectorShopeeAccount(http.Controller):
#     @http.route('/connector_shopee_account/connector_shopee_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/connector_shopee_account/connector_shopee_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('connector_shopee_account.listing', {
#             'root': '/connector_shopee_account/connector_shopee_account',
#             'objects': http.request.env['connector_shopee_account.connector_shopee_account'].search([]),
#         })

#     @http.route('/connector_shopee_account/connector_shopee_account/objects/<model("connector_shopee_account.connector_shopee_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('connector_shopee_account.object', {
#             'object': obj
#         })