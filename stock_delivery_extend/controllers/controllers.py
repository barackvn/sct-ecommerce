# -*- coding: utf-8 -*-
from odoo import http

# class StockPickingBarcode(http.Controller):
#     @http.route('/stock_picking_barcode/stock_picking_barcode/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_picking_barcode/stock_picking_barcode/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_picking_barcode.listing', {
#             'root': '/stock_picking_barcode/stock_picking_barcode',
#             'objects': http.request.env['stock_picking_barcode.stock_picking_barcode'].search([]),
#         })

#     @http.route('/stock_picking_barcode/stock_picking_barcode/objects/<model("stock_picking_barcode.stock_picking_barcode"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_picking_barcode.object', {
#             'object': obj
#         })