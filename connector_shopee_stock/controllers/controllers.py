# -*- coding: utf-8 -*-
from odoo import http
#from odoo.addons.shopee_api_client.controllers.controllers import ShopeeApiClient

#class ShopeeApiClientStock(ShopeeApiClient):
#    @http.route('/shopee_client/shop/<model("shopee_client.shop"):shop>/order_tracking_no', methods=['POST'], auth='public',csrf=False)
#    def order_tracking_no(self,shop, **kw):
#        if shop.sudo().order_tracking_no_push(kw.get('ordersn'), kw.get('trackingno')):
#            return http.Response(status=200)
#        else:
#            return http.Response(status=500)

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
