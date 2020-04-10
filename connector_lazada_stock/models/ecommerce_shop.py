# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta
import logging
_logger= logging.getLogger(__name__)

class eCommerceShop(models.Model):
    _inherit = 'ecommerce.shop'

#    def order_tracking_no_push(self, ordersn, tracking_no):
#        self.env['sale.order'].search([('ecommerce_shop_id','=',self.id),('client_order_ref','=',ordersn)])[:1].picking_ids.write({
#            'carrier_tracking_ref': tracking_no,
#            })
#        return True

    def _create_order_lazada(self, order, detail=False):
        detail = detail or self._py_client_lazada_request('/order/items/get','GET', order_id = order['order_id']).get('data')
        sale_order = super(eCommerceShop, self)._create_order_lazada(order, detail=detail)
        for line in sale_order.order_line:
            if order.get('warehouse_code') == 'dropshipping':
                line.route_id = self.env.ref('connector_lazada_stock.stock_location_route_lazada_transit')
            elif order.get('warehouse_code','').startswith('OMS-LAZADA'):
                line.route_id = self.env.ref('connector_lazada_stock.stock_location_route_lazada_fbl')
        return sale_order

    def _update_order_lazada(self, order, statuses=[], detail=False):
        detail = detail or self._py_client_lazada_request('/order/items/get','GET', order_id = order.client_order_ref).get('data')
        order = super(eCommerceShop, self)._update_order_lazada(order, statuses=statuses, detail=detail)
        for status in statuses:
            if status in ['ready_to_ship','shipped']:
                if not order.carrier_id: 
                    order.carrier_id = self.env['ecommerce.carrier'].search([
                        ('name','=', detail[0].get('shipment_provider','').split('Delivery: ')[-1])
                    ])[:1].carrier_id
                    picks = order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'])
                    picks.write({
                        'carrier_id': order.carrier_id.id,
                        'carrier_tracking_ref': detail[0].get('tracking_code','')
                    })
            elif status in ['returned', 'failed']: 
                pick_ids = order.picking_ids.filtered(lambda r: r.picking_type_id in [self.env.ref('connector_lazada_stock.stock_picking_type_lazada_out'), order.warehouse_id.out_type_id])
                for pick_id in pick_ids: 
                    if pick_id.state not in ['done','cancel']: pick_id.action_cancel()
                    elif pick_id.state == 'done': 
                        wiz = self.env['stock.picking.return'].create({'picking_id': pick_id.id})
                        wiz.product_return_moves.write({'to_refund': True})
                        wiz.create_returns()

            elif status == 'delivered':
                pick_ids = order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'] and r.picking_type_id in [self.env.ref('connector_lazada_stock.stock_picking_type_lazada_out'), self.env.ref('connector_lazada_stock.stock_picking_type_lazada_in')])
                for pick_id in pick_ids:
                    for line in pick_id.move_line_ids: 
                        if line.state not in ['done', 'cancel']: line.qty_done = line.product_uom_qty
                    self.env['stock.immediate.transfer'].create({'pick_ids': [(4, pick_id.id)]}).process()
        return order

    def _get_logistic_lazada(self):
        self.ensure_one()
        logistics = self._py_client_lazada_request('/shipment/providers/get','GET').get('data',{}).get('shipment_providers')
        for l in logistics:
            self.env['ecommerce.shop.carrier'].create({
                'ecomm_carrier_id': self.env['ecommerce.carrier'].search([
                    ('platform_id','=',self.platform_id.id),
                    ('name', '=', l.get('name'))
                ])[:1].id,
                'shop_id': self.id,
                'default': l.get('is_default'),
                'cod': l.get('cod'),
                })
