# -*- coding: utf-8 -*-
from odoo import http

class ShopeeApiClient(http.Controller):
    @http.route('/shopee_client/shop/<model("shopee_client.shop"):shop>/auth', methods=['POST'], auth='public',csrf=False)
    def auth_push(self,shop, **kw):
        if shop.sudo().write(kw):
            return http.Response(status=200)
        else:
            return http.Response(status=500)


    @http.route('/shopee_client/shop/<model("shopee_client.shop"):shop>/order_status', methods=['POST'], auth='public',csrf=False)
    def order_status(self,shop, **kw):
        if shop.sudo().order_status_push(kw.get('ordersn'), kw.get('status'),kw.get('update_time')):
            return http.Response(status=200)
        else:
            return http.Response(status=500)
    
    @http.route('/shopee_client/shop/<model("shopee_client.shop"):shop>/order_tracking_no', methods=['POST'], auth='public',csrf=False)
    def order_tracking_no(self,shop, **kw):
        return http.Response(status=200)
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shopee_api_client/shopee_api_client/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('shopee_api_client.listing', {
#             'root': '/shopee_api_client/shopee_api_client',
#             'objects': http.request.env['shopee_api_client.shopee_api_client'].search([]),
#         })

#     @http.route('/shopee_api_client/shopee_api_client/objects/<model("shopee_api_client.shopee_api_client"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shopee_api_client.object', {
#             'object': obj
#         })
