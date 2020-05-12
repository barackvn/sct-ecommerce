# -*- coding: utf-8 -*-
from odoo import http

# class ConnectorLazadaAccount(http.Controller):
#     @http.route('/connector_lazada_account/connector_lazada_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/connector_lazada_account/connector_lazada_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('connector_lazada_account.listing', {
#             'root': '/connector_lazada_account/connector_lazada_account',
#             'objects': http.request.env['connector_lazada_account.connector_lazada_account'].search([]),
#         })

#     @http.route('/connector_lazada_account/connector_lazada_account/objects/<model("connector_lazada_account.connector_lazada_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('connector_lazada_account.object', {
#             'object': obj
#         })