# -*- coding: utf-8 -*-
from odoo import http
import hmac, hashlib, json
import logging

_logger = logging.getLogger(__name__)
PARAMS = {
    "partner_id": "shopee_api_server.shopee_partner_id",
    "key": "shopee_api_server.shopee_partner_key",
}

class ShopeeApiServer(http.Controller):
    @http.route('/shopee_api_server/shopee_shop/<model("shopee_api_server.shopee_shop"):shop>/retrieve/', auth='public')
    def retrieve_shop_id(self, shop,**kw):
        #fix security later
        shop = shop.sudo()

        shops = http.request.env['shopee_api_server.shopee_shop'].sudo().search([('shop_id','=',kw.get('shop_id'))])
        if shops and shops[0] != shop:
            shop.unlink()
            shop = shops[0]
        kw.update({'state': 'auth'})
        shop.write(dict(kw))
        _vals = {'code': 1, 'shop_id':kw.get('shop_id')}
        shop.handle_push(_vals)
        return 'Successful!'


    @http.route('/shopee_api_server/shopee_shop/request', type='http', methods=['POST'], auth='public', csrf=False)
    def reg_request(self, token=True, **kw):
        if token:
            shop = http.request.env['shopee_api_server.shopee_shop'].sudo().handle_reg_request(kw)
            return shop and shop.authorize_url


    @http.route('/shopee_api_server/shopee_shop/postman', type='json', methods=['POST'], auth='public')
    def handle_post(self, **kw):
        url = http.request.httprequest.url
        json_data = http.request.jsonrequest 
        request_body = json.dumps(json_data) 
        partner_key = http.request.env['ir.config_parameter'].sudo().get_param(PARAMS['key'], '')
        authorization = http.request.httprequest.environ.get('HTTP_AUTHORIZATION')
#        _logger.info(http.request.__dict__)
#        _logger.info(http.request.httprequest.__dict__)
        _logger.info(url,request_body, partner_key, authorization)

        base_string = url + '|' + request_body
        cal_auth = hmac.new(partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        if cal_auth != authorization:
            http.request.env['shopee_api_server.shopee_shop'].sudo().search([('shop_id','=',json_data.get('shop_id'))]).handle_push(json_data)
            _logger.info(json_data)
            return http.Response(status=202)
        else:
            return http.Response(status=500)
 

#     @http.route('/shopee_api_server/shopee_api_server/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('shopee_api_server.listing', {
#             'root': '/shopee_api_server/shopee_api_server',
#             'objects': http.request.env['shopee_api_server.shopee_api_server'].search([]),
#         })

#     @http.route('/shopee_api_server/shopee_api_server/objects/<model("shopee_api_server.shopee_api_server"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shopee_api_server.object', {
#             'object': obj
#         })
