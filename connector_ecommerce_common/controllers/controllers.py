# -*- coding: utf-8 -*-
from odoo import http
import hmac, hashlib, json
import logging

_logger = logging.getLogger(__name__)

class eCommerceController(http.Controller):
    @http.route('/connector_ecommerce/<model("ecommerce.platform"):platform>/webhook_endpoint', type='json', methods=['POST'], auth='public')
    def webhook(self, platform, **kw):
        getattr(self, "_webhook_{}".format(platform.platform))(platform, **kw)

#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_ecommerce_client/base_ecommerce_client/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_ecommerce_client.listing', {
#             'root': '/base_ecommerce_client/base_ecommerce_client',
#             'objects': http.request.env['base_ecommerce_client.base_ecommerce_client'].search([]),
#         })

#     @http.route('/base_ecommerce_client/base_ecommerce_client/objects/<model("base_ecommerce_client.base_ecommerce_client"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_ecommerce_client.object', {
#             'object': obj
#         })
