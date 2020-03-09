# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.connector_ecommerce_common.controllers.controllers import eCommerceController
import hmac, hashlib, json
import logging

_logger = logging.getLogger(__name__)

class ShopeeController(eCommerceController):
    
    def _webhook_shopee(self, platform,**kw):
        url = http.request.httprequest.url
        json_data = http.request.jsonrequest
        request_body = json.dumps(json_data)
        authorization = http.request.httprequest.environ.get('HTTP_AUTHORIZATION')
        base_string = url + '|' + request_body
        cal_auth = hmac.new(platform.key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        #_logger.info(cal_auth)
        #if cal_auth == authorization:
        if True:
            if json_data.get('code',0) == 3:
                data = json_data.get("data",{})
                http.request.env['ecommerce.shop'].sudo().search([
                    ('platform_id','=',platform.id),
                    ('ecomm_shop_idn','=', json_data.get('shop_id'))
                    ])._order_status_push_shopee(data.get('ordersn'), data.get('status'),data.get('update_time'))
            return http.Response(status=202)
        else:
            return http.Response(status=500)

#class ShopeeController(http.Controller):
#    @http.route('/ecommerce/shopee/shop/<model("shopee_server.shop"):shop>/retrieve/', auth='public')
#    def retrieve_shop_id(self, shop,**kw):
#        #fix security later
#        shop = shop.sudo()
#
#        shops = http.request.env['shopee_server.shop'].sudo().search([('shop_id','=',kw.get('shop_id'))])
#        if shops and shops[0] != shop:
#            shop.unlink()
#            shop = shops[0]
#        kw.update({'state': 'auth'})
#        shop.write(dict(kw))
#        _vals = {'code': 1, 'shop_id':kw.get('shop_id')}
#        shop.handle_push(_vals)
#        return 'Successful!'


#    @http.route('/shopee_server/shop/request', type='http', methods=['POST'], auth='public', csrf=False)
#    def reg_request(self, token=True, **kw):
#        if token:
#            shop = http.request.env['shopee_server.shop'].sudo().handle_reg_request(kw)
#            return shop and shop.authorize_url

#        _logger.info(http.request.__dict__)
#        _logger.info(http.request.httprequest.__dict__)
#     @http.route('/shopee_server/shopee_server/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('shopee_server.listing', {
#             'root': '/shopee_server/shopee_server',
#             'objects': http.request.env['shopee_server.shopee_server'].search([]),
#         })

#     @http.route('/shopee_server/shopee_server/objects/<model("shopee_server.shopee_server"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shopee_server.object', {
#             'object': obj
#         })
