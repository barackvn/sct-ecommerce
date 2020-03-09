# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta
import logging
_logger= logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    need_tracking_no = fields.Boolean()

class eCommerceShop(models.Model):
    _inherit = 'ecommerce.shop'

#    def order_tracking_no_push(self, ordersn, tracking_no):
#        self.env['sale.order'].search([('ecommerce_shop_id','=',self.id),('client_order_ref','=',ordersn)])[:1].picking_ids.write({
#            'carrier_tracking_ref': tracking_no,
#            })
#        return True

    def _new_order_shopee(self, ordersn, status, update_time):
        order = super(eCommerceShop, self)._new_order_shopee(ordersn, status, update_time)
        for line in order.order_line:
            line.route_id = self.env.ref('connector_shopee_stock.stock_location_route_shopee')
        return order

    def _update_order_shopee(self, ordersn, status, update_time):
        order = super(eCommerceShop, self)._update_order_shopee(ordersn, status, update_time)
        if status in ['READY_TO_SHIP','RETRY_SHIP']:
            order.need_tracking_no = True

        elif status == 'TO_CONFIRM_RECEIVE':
            shopee_pick_ids = order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'] and r.picking_type_id == self.env.ref('connector_shopee_stock.stock_picking_type_shopee_out'))
            for pick_id in shopee_pick_ids: 
                for line in pick_id.move_line_ids: 
                    if line not in ['done', 'cancel']: line.qty_done = line.product_uom_qty
                self.env['stock.immediate.transfer'].create({'pick_ids': [(4, pick_id.id)]}).process()

        elif status == 'TO_RETURN': 
            pick_ids = order.picking_ids.filtered(r.picking_type_id in [self.env.ref('connector_shopee_stock.stock_picking_type_shopee_out'), order.warehouse_id.out_type_id])
            for pick_id in pick_ids: 
                if pick_id.state not in ['done','cancel']: pick_id.action_cancel()
                elif pick_id.state == 'done': 
                    wiz = self.env['stock.picking.return'].create({'picking_id': pick_id.id})
                    wiz.product_return_moves.write({'to_refund': True})
                    wiz.create_returns()

        elif status == 'COMPLETED':
            pick_ids = order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'] and r.picking_type_id in [self.env.ref('connector_shopee_stock.stock_picking_type_shopee_out'), self.env.ref('connector_shopee_stock.stock_picking_type_shopee_in')])
            for pick_id in pick_ids:
                for line in pick_id.move_line_ids: 
                    if line not in ['done', 'cancel']: line.qty_done = line.product_uom_qty
                self.env['stock.immediate.transfer'].create({'pick_ids': [(4, pick_id.id)]}).process()
        return order

    @api.model
    def get_tracking_no(self):
        orders = self.env['sale.order'].search([
            ('ecommerce_shop_id.platform_id.platform','=','shopee'),
            ('state','=', 'sale'),
            ('need_tracking_no','=',True),
            ('confirmation_date','>',(datetime.now()-timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S"))
            ], limit=100)
        for order in orders:
            logistic = order.ecommerce_shop._py_client_shopee().logistic.get_order_logistic(ordersn=order.client_order_ref).get('logistics')
            if logistic:
                order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel']).write({
                    'carrier_tracking_ref': logistic['tracking_no'],
                    })
                order.need_tracking_no = False