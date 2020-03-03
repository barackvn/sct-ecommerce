# -*- coding: utf-8 -*-
from odoo import http

# class ShopeeEcommerceClient(http.Controller):
#     @http.route('/shopee_ecommerce_client/shopee_ecommerce_client/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shopee_ecommerce_client/shopee_ecommerce_client/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('shopee_ecommerce_client.listing', {
#             'root': '/shopee_ecommerce_client/shopee_ecommerce_client',
#             'objects': http.request.env['shopee_ecommerce_client.shopee_ecommerce_client'].search([]),
#         })

#     @http.route('/shopee_ecommerce_client/shopee_ecommerce_client/objects/<model("shopee_ecommerce_client.shopee_ecommerce_client"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shopee_ecommerce_client.object', {
#             'object': obj
#         })