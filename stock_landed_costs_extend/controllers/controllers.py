# -*- coding: utf-8 -*-
from odoo import http

# class StockLandedCostsExtend(http.Controller):
#     @http.route('/stock_landed_costs_extend/stock_landed_costs_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_landed_costs_extend/stock_landed_costs_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_landed_costs_extend.listing', {
#             'root': '/stock_landed_costs_extend/stock_landed_costs_extend',
#             'objects': http.request.env['stock_landed_costs_extend.stock_landed_costs_extend'].search([]),
#         })

#     @http.route('/stock_landed_costs_extend/stock_landed_costs_extend/objects/<model("stock_landed_costs_extend.stock_landed_costs_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_landed_costs_extend.object', {
#             'object': obj
#         })