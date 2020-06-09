# -*- coding: utf-8 -*-
from odoo import http

# class DeliveryEcommerceCommon(http.Controller):
#     @http.route('/delivery_ecommerce_common/delivery_ecommerce_common/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/delivery_ecommerce_common/delivery_ecommerce_common/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('delivery_ecommerce_common.listing', {
#             'root': '/delivery_ecommerce_common/delivery_ecommerce_common',
#             'objects': http.request.env['delivery_ecommerce_common.delivery_ecommerce_common'].search([]),
#         })

#     @http.route('/delivery_ecommerce_common/delivery_ecommerce_common/objects/<model("delivery_ecommerce_common.delivery_ecommerce_common"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('delivery_ecommerce_common.object', {
#             'object': obj
#         })