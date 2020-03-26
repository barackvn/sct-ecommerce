# -*- coding: utf-8 -*-
from odoo import http

# class ConnectorLazadaStock(http.Controller):
#     @http.route('/connector_lazada_stock/connector_lazada_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/connector_lazada_stock/connector_lazada_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('connector_lazada_stock.listing', {
#             'root': '/connector_lazada_stock/connector_lazada_stock',
#             'objects': http.request.env['connector_lazada_stock.connector_lazada_stock'].search([]),
#         })

#     @http.route('/connector_lazada_stock/connector_lazada_stock/objects/<model("connector_lazada_stock.connector_lazada_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('connector_lazada_stock.object', {
#             'object': obj
#         })