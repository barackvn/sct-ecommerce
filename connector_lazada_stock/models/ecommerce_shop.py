# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta
from PyPDF2 import PdfFileWriter, PdfFileReader
import base64, io
import logging
_logger= logging.getLogger(__name__)

class eCommerceShop(models.Model):
    _inherit = 'ecommerce.shop'

#    def order_tracking_no_push(self, ordersn, tracking_no):
#        self.env['sale.order'].search([('ecommerce_shop_id','=',self.id),('client_order_ref','=',ordersn)])[:1].picking_ids.write({
#            'carrier_tracking_ref': tracking_no,
#            })
#        return True

    def _get_orders_detail_lazada(self, lazada_orders):
        zip_orders = super(eCommerceShop, self)._get_orders_detail_lazada(lazada_orders)
        to_update_pairs = [(d, d['order_items'][0]['order_item_id']) for o, d in zip_orders if d['order_items'][0].get('tracking_code')]
        if not to_update_pairs:
            return zip_orders
        orders_detail, order_item_ids = zip(*to_update_pairs)
        resp = self._py_client_lazada_request('/order/document/get', 'GET', doc_type='shippingLabel', order_item_ids=str(list(order_item_ids)))
        if not resp.get('data'):
            return zip_orders
        raw = resp['data']['document']['file']
        Report = self.env['ir.actions.report']
        stream = io.BytesIO(Report._run_wkhtmltopdf([base64.b64decode(raw)]))
        streams = [stream]
        pdf = PdfFileReader(stream)
        for page in range(pdf.getNumPages()):
            writer = PdfFileWriter()
            writer.addPage(pdf.getPage(page))
            res_stream = io.BytesIO()
            streams.append(res_stream)
            writer.write(res_stream)
            orders_detail[page]['order_items'][0]['shippingLabel'] = base64.encodestring(res_stream.getvalue())
        for stream in streams:
            try:
                stream.close()
            except Exception:
                pass
        return zip_orders

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
        report = self.env['ir.actions.report']._get_report_from_name('stock.report_deliveryslip')
        detail = detail or self._py_client_lazada_request('/order/items/get','GET', order_id = order.client_order_ref).get('data')
        order = super(eCommerceShop, self)._update_order_lazada(order, statuses=statuses, detail=detail)
        for status in statuses:
            if status in ['pending','ready_to_ship','shipped']:
                order.invoice_shipping_on_delivery = False
                #tracking code generated mean delivery info is ready
                if not detail[0].get('tracking_code'):
                    continue
                if not order.carrier_id: 
                    order.carrier_id = self.env['ecommerce.carrier'].search([
                        ('name','=', detail[0].get('shipment_provider','').split('Delivery: ')[-1])
                    ])[:1].carrier_id
                    picks = order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'])
                    picks.write({
                        'carrier_id': order.carrier_id.id,
                        'carrier_tracking_ref': detail[0].get('tracking_code','')
                    })
                start_picking = order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'] and r.picking_type_id == order.warehouse_id.out_type_id)[:1]
                if not start_picking or start_picking.ecomm_delivery_slip_loaded:
                    continue
                report.render(start_picking.ids)
                attachment = report.retrieve_attachment(start_picking)
                if attachment:
                    streams = [io.BytesIO(base64.decodestring(attachment.datas)), io.BytesIO(base64.decodestring(detail[0]['shippingLabel']))]
                    writer = PdfFileWriter()
                    for stream in streams:
                        writer.appendPagesFromReader(PdfFileReader(stream))
                    if writer.getNumPages()%2 == 1:
                        writer.addBlankPage()
                    res_stream = io.BytesIO()
                    streams.append(res_stream)
                    writer.write(res_stream)
                    try:
                        attachment.write({
                            'datas': base64.encodestring(res_stream.getvalue()),
                            'datas_fname': attachment.name
                            })
                    except exceptions.AccessError:
                        _logger.info("Cannot save PDF report")
                    finally:
                        start_picking.ecomm_delivery_slip_loaded = True
                        for stream in streams:
                            try:
                                stream.close()
                            except Exception:
                                pass

            elif status in ['returned', 'failed', 'cancel']:
                pick_ids = order.picking_ids.filtered(lambda r: r.picking_type_id == self.env.ref('connector_lazada_stock.stock_picking_type_lazada_out')) + order.picking_ids.filtered(lambda r: r.picking_type_id == order.warehouse_id.out_type_id)
                for pick_id in pick_ids:
                    if pick_id.state not in ['done','cancel']: pick_id.action_cancel()
                    elif pick_id.state == 'done':
                        returns = order.picking_ids.filtered(lambda r: r.location_id == pick_id.location_dest_id and r.location_dest_id == pick_id.location_id and r.state != 'cancel')
                        if not returns:
                            wiz_model = self.env['stock.return.picking']
                            wiz = wiz_model.create(wiz_model.with_context(active_id = pick_id.id).default_get(wiz_model._fields.keys()))
                            wiz.product_return_moves.write({'to_refund': True})
                            new_picking_id, pick_type_id = wiz._create_returns()
                            return_pick = self.env['stock.picking'].browse(new_picking_id)
                            return_pick.write({
                                'carrier_id': pick_id.carrier_id.id,
                                'carrier_tracking_ref': pick_id.carrier_tracking_ref
                                })
                            for moves in zip(pick_id.move_lines, return_pick.move_lines):
                                l = len(moves[1].move_line_ids)
                                moves[1].write({
                                    'move_line_ids': [(1, moves[1].move_line_ids[i].id, {
                                        'lot_id': v.lot_id and v.lot_id.id
                                    }) for i,v in enumerate(moves[0].move_line_ids[:l])] + [(0, _, {
                                        'product_uom_id': moves[1].product_uom.id,
                                        'picking_id': moves[1].picking_id.id,
                                        'move_id': moves[1].id,
                                        'product_id': moves[1].product_id.id,
                                        'location_id': moves[1].location_id.id,
                                        'location_dest_id': moves[1].location_dest_id.id,
                                        'lot_id': v.lot_id and v.lot_id.id
                                    }) for i,v in enumerate(moves[0].move_line_ids[l:])]
                                })
                for line in order.order_line:
                    line.product_uom_qty = line.qty_delivered

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
            carrier = self.env['ecommerce.shop.carrier'].search([
                ('shop_id', '=', self.id),
                ('name','=',l.get('name')),
            ])
            if carrier:
                carrier[0].write({
                    'enable': l.get('enabled'),
                    'default': l.get('preferred'),
                    'cod': l.get('has_cod'),
                })
            else:
                self.env['ecommerce.shop.carrier'].create({
                    'ecomm_carrier_id': self.env['ecommerce.carrier'].search([
                        ('platform_id','=', self.platform_id.id),
                        ('name','=',l.get('name')),
                    ])[:1].id or self.env['ecommerce.carrier'].create({
                        'name': l.get('name'),
                        'platform_id': self.platform_id.id,
                        'carrier_id' : self.env['delivery.carrier'].create({
                            'name': l.get('name'),
                            'product_id': self.env.ref('delivery.product_product_delivery').id
                        }).id
                    }).id,
                    'shop_id': self.id,
                    'default': l.get('preferred'),
                    'cod': l.get('has_cod'),
                })
