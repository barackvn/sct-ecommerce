# -*- coding: utf-8 -*-
from odoo import http

# class ConnectorTikiStock(http.Controller):
#     @http.route('/connector_tiki_stock/connector_tiki_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/connector_tiki_stock/connector_tiki_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('connector_tiki_stock.listing', {
#             'root': '/connector_tiki_stock/connector_tiki_stock',
#             'objects': http.request.env['connector_tiki_stock.connector_tiki_stock'].search([]),
#         })

#     @http.route('/connector_tiki_stock/connector_tiki_stock/objects/<model("connector_tiki_stock.connector_tiki_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('connector_tiki_stock.object', {
#             'object': obj
#         })