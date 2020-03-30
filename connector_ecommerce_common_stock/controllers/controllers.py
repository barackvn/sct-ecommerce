# -*- coding: utf-8 -*-
from odoo import http

# class ConnectorEcommerceCommonStock(http.Controller):
#     @http.route('/connector_ecommerce_common_stock/connector_ecommerce_common_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/connector_ecommerce_common_stock/connector_ecommerce_common_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('connector_ecommerce_common_stock.listing', {
#             'root': '/connector_ecommerce_common_stock/connector_ecommerce_common_stock',
#             'objects': http.request.env['connector_ecommerce_common_stock.connector_ecommerce_common_stock'].search([]),
#         })

#     @http.route('/connector_ecommerce_common_stock/connector_ecommerce_common_stock/objects/<model("connector_ecommerce_common_stock.connector_ecommerce_common_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('connector_ecommerce_common_stock.object', {
#             'object': obj
#         })