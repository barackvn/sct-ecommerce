# -*- coding: utf-8 -*-
from odoo import http

# class ConnectorTiki(http.Controller):
#     @http.route('/connector_tiki/connector_tiki/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/connector_tiki/connector_tiki/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('connector_tiki.listing', {
#             'root': '/connector_tiki/connector_tiki',
#             'objects': http.request.env['connector_tiki.connector_tiki'].search([]),
#         })

#     @http.route('/connector_tiki/connector_tiki/objects/<model("connector_tiki.connector_tiki"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('connector_tiki.object', {
#             'object': obj
#         })