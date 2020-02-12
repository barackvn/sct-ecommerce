# -*- coding: utf-8 -*-
from odoo import http

# class ShopeeApiClientStock(http.Controller):
#     @http.route('/shopee_api_client_stock/shopee_api_client_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shopee_api_client_stock/shopee_api_client_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('shopee_api_client_stock.listing', {
#             'root': '/shopee_api_client_stock/shopee_api_client_stock',
#             'objects': http.request.env['shopee_api_client_stock.shopee_api_client_stock'].search([]),
#         })

#     @http.route('/shopee_api_client_stock/shopee_api_client_stock/objects/<model("shopee_api_client_stock.shopee_api_client_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shopee_api_client_stock.object', {
#             'object': obj
#         })