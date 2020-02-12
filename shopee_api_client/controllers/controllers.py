# -*- coding: utf-8 -*-
from odoo import http
import logging
_logger = logging.getLogger(__name__)

class ShopeeApiClient(http.Controller):
    @http.route('/shopee_api_client/shopee_shop/<model("shopee_api_client.shopee_shop"):shop>/auth', methods=['POST'], auth='public',csrf=False)
    def auth_push(self,shop, **kw):
        if shop.sudo().write(kw):
            shop.getPyClient()
            return http.Response(status=200)
        else:
            return http.Response(status=500)


    @http.route('/shopee_api_client/shopee_shop/<model("shopee_api_client.shopee_shop"):shop>/order', methods=['POST'], auth='public',csrf=False)
    def order_push(self,shop, **kw):
        if shop.sudo().order_push(kw.get('ordersn'), kw.get('status'),kw.get('update_time')):
        #if shop.sudo().write(kw):
            return http.Response(status=200)
        else:
            return http.Response(status=500)
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
