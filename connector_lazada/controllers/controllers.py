# -*- coding: utf-8 -*-
from odoo import http

class ConnectorLazada(http.Controller):

    @http.route('/connector_ecommerce/<model("ecommerce.shop"):shop>/auth', auth='public')
    def auth_callback(self, shop, **kw):
        #fix security later
        if kw.get('code'):
            shop= shop.sudo()
            resp = shop._py_client_lazada_request('/auth/token/create',code=kw.get('code'))
            if resp['code'] = 'MissingParameter':
                return 'Fail to authorize'
            elif resp['account_id']:
                shop.write({
                    'access_token': resp.get('access_token'),
                    'refresh_token': resp.get('refresh_token'),
                    'refresh_expires_in': resp.get('refresh_expires_in'),
                    'account': resp.get('account')
                    })
        #shop.write({
        #    'ecomm_shop_idn': kw.get('shop_id'),
        #    'state': 'auth'})
                shop._get_info_lazada()
                return 'Successfully authorized!'

#     @http.route('/connector_lazada/connector_lazada/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/connector_lazada/connector_lazada/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('connector_lazada.listing', {
#             'root': '/connector_lazada/connector_lazada',
#             'objects': http.request.env['connector_lazada.connector_lazada'].search([]),
#         })

#     @http.route('/connector_lazada/connector_lazada/objects/<model("connector_lazada.connector_lazada"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('connector_lazada.object', {
#             'object': obj
#         })
