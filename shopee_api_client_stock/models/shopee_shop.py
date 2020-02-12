# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ShopeeClientShop(models.Model):
    _inherit = 'shopee_client.shop'

    def new_order(self, ordersn, status, update_time):
        order = super(ShopeeClientShop, self).new_order(ordersn, status, update_time)
        for line in order.order_line:
            line.route_id = self.env.ref('shopee_api_client_stock.stock_location_route_shopee')
        return order

    def update_order(self, ordersn, status, update_time):
        order = super(ShopeeClientShop, self).update_order(ordersn, status, update_time)
        if status == 'TO_CONFIRM_RECEIVE':
            shopee_pick_ids = order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'] and r.picking_type_id == self.env.ref('shopee_api_client_stock.stock_picking_type_shopee_out'))
            for pick_id in shopee_pick_ids: 
                wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, pick_id.id)]}).process()
        elif status == 'TO_RETURN': 
            shopee_pick_ids = order.picking_ids.filtered(r.picking_type_id == self.env.ref('shopee_api_client_stock.stock_picking_type_shopee_out'))
            for pick_id in shopee_pick_ids: 
                if pick_id.state not in ['done','cancel']: pick_id.action_cancel()
                elif pick_id.state == 'done': wiz = self.env['stock.picking.return'].create({'picking_id': pick_id.id}).create_returns()
            wh_pick_ids = order.picking_ids.filtered(lambda r: r.state == 'done' and r.picking_type_id == order.warehouse_id.out_type_id)
            for pick_id in wh_pick_ids: 
                wiz = self.env['stock.picking.return'].create({'picking_id': pick_id.id}).create_returns()
        elif status == 'COMPLETED':
            pick_ids = order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'] and r.picking_type_id in [self.env.ref('shopee_api_client_stock.stock_picking_type_shopee_out'), self.env.ref('shopee_api_client_stock.stock_picking_type_shopee_in'))
            for pick_id in pick_ids:
                wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, pick_id.id)]}).process()
        return order

