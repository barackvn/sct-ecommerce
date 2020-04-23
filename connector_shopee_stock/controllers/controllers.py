# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.connector_shopee.controllers.controllers import ShopeeController

class ShopeeController(ShopeeController):
    def _solver_shopee(self,platform, json_data={}):
        if not super(ShopeeController, self)._solver_shopee(platform, json_data=json_data):
            if json_data.get('code',0) == 4:
                data = json_data.get("data",{})
                http.request.env['ecommerce.shop'].sudo().search([
                    ('platform_id','=',platform.id),
                    ('ecomm_shop_idn','=', json_data.get('shop_id'))
                ])._order_tracking_push_shopee(data.get('ordersn'), data.get('trackingno'))
                return True
            else:
                return False
        else:
            return True

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
