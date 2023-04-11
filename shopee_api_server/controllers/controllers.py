# -*- coding: utf-8 -*-
from odoo import http
import hmac, hashlib, json
import logging

_logger = logging.getLogger(__name__)
PARAMS = {
    "partner_id": "shopee_server.shopee_partner_id",
    "key": "shopee_server.shopee_partner_key",
}

class ShopeeApiServer(http.Controller):
    @http.route('/shopee_server/shop/<model("shopee_server.shop"):shop>/retrieve/', auth='public')
    def retrieve_shop_id(self, shop,**kw):
        #fix security later
        shop = shop.sudo()

        shops = http.request.env['shopee_server.shop'].sudo().search([('shop_id','=',kw.get('shop_id'))])
        if shops and shops[0] != shop:
            shop.unlink()
            shop = shops[0]
        kw['state'] = 'auth'
        shop.write(dict(kw))
        _vals = {'code': 1, 'shop_id':kw.get('shop_id')}
        shop.handle_push(_vals)
        return 'Successful!'


    @http.route('/shopee_server/shop/request', type='http', methods=['POST'], auth='public', csrf=False)
    def reg_request(self, token=True, **kw):
        if token:
            shop = http.request.env['shopee_server.shop'].sudo().handle_reg_request(kw)
            return shop and shop.authorize_url


    @http.route('/shopee_server/shop/postman', type='json', methods=['POST'], auth='public')
    def handle_post(self, **kw):
        url = http.request.httprequest.url
        #url = http.request.httprequest.environ.get('HTTP_HOST')+ http.request.httprequest.environ.get('PATH_INFO')
        #_logger.info(url)
        json_data = http.request.jsonrequest
        #_logger.info(http.request.__dict__)
        request_body = json.dumps(json_data)
        #_logger.info(request_body)
        partner_key = http.request.env['ir.config_parameter'].sudo().get_param(PARAMS['key'], '')
        authorization = http.request.httprequest.environ.get('HTTP_AUTHORIZATION')
        #_logger.info(authorization)
        base_string = f'{url}|{request_body}'
        cal_auth = hmac.new(partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        _logger.info(json_data)
        http.request.env['shopee_server.shop'].sudo().search([('shop_id','=',json_data.get('shop_id'))]).handle_push(json_data)
        return http.Response(status=202)
 

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
