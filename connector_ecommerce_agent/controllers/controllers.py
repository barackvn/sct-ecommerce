# -*- coding: utf-8 -*-
from odoo import http
import hmac, hashlib, json
import logging

_logger = logging.getLogger(__name__)

class eCommerceController(http.Controller):
    @http.route('/connector_ecommerce/<model("ecommerce.platform"):platform>/webhook_endpoint', type='json', methods=['POST'], auth='public')
    def webhook(self, platform, **kw):
        getattr(self, "_webhook_{}".format(platform.platform)(platform, **kw)
# class ConnectorEcommerceAgent(http.Controller):
#     @http.route('/connector_ecommerce_agent/connector_ecommerce_agent/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/connector_ecommerce_agent/connector_ecommerce_agent/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('connector_ecommerce_agent.listing', {
#             'root': '/connector_ecommerce_agent/connector_ecommerce_agent',
#             'objects': http.request.env['connector_ecommerce_agent.connector_ecommerce_agent'].search([]),
#         })

#     @http.route('/connector_ecommerce_agent/connector_ecommerce_agent/objects/<model("connector_ecommerce_agent.connector_ecommerce_agent"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('connector_ecommerce_agent.object', {
#             'object': obj
#         })
