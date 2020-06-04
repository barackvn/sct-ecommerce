#-*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import base64, io, requests
from PyPDF2 import PdfFileMerger, PdfFileReader
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def _sync_tracking_ref_shopee(self):
        #eCommerceShop = self.env['ecommerce.shop']
        report = self.env['ir.actions.report']._get_report_from_name('stock.report_deliveryslip')
        '''shop:{ref:[p,p1]}'''
        shops_dict = {}
        for p in self:
            if not p.ecommerce_shop_id:
                continue
            if shops_dict.get(p.ecommerce_shop_id):
                if  shops_dict[p.ecommerce_shop_id].get(p.sale_id.client_order_ref):
                    shops_dict[p.ecommerce_shop_id][p.sale_id.client_order_ref] |= p
                else:
                    shops_dict[p.ecommerce_shop_id][p.sale_id.client_order_ref] = p
            else:
                shops_dict[p.ecommerce_shop_id] = {p.sale_id.client_order_ref: p}
        _logger.info(shops_dict)
        for shop, pickings_dict in shops_dict.items():
            #shop = eCommerceShop.browse(shop_id)
            #pickings_dict = {p.sale_id.client_order_ref: p for p in self if p.ecommerce_shop_id == shop}
            ordersn_list = list(pickings_dict.keys())
            tracks =[]
            for i in range(0,len(ordersn_list),20):
                tracks += shop._py_client_shopee().logistic.get_tracking_no(ordersn_list=ordersn_list[i:i+20]).get('result',{}).get('orders',[])
            awbs = []
            for i in range(0,len(ordersn_list),50):
                awbs += shop._py_client_shopee().logistic.get_airway_bill(ordersn_list=ordersn_list[i:i+50], is_batch=False).get('result',{}).get('airway_bills',[])
            for o in tracks:
                pickings = pickings_dict[o['ordersn']]
                vals = {
                    'carrier_tracking_ref': o['tracking_no'],
                    'carrier_id': self.env['ecommerce.carrier'].search([
                        ('platform_id','=',shop.platform_id.id),
                        ('name','=', o['shipping_carrier'])
                    ])[:1].carrier_id.id,
                }
                pickings.write(vals)
            for o in awbs:
                pickings = pickings_dict[o['ordersn']]
                for picking in pickings:
                    if picking.ecomm_delivery_slip_loaded:
                        continue
                    report.render(picking.ids)
                    attachment = report.retrieve_attachment(picking)
                    if attachment:
                        merger = PdfFileMerger()
                        merger.append(io.BytesIO(base64.decodestring(attachment.datas)), import_bookmarks=False)
                        merger.append(io.BytesIO(requests.get(o['airway_bill']).content), import_bookmarks=False)
                        buff = io.BytesIO()
                        try:
                            merger.write(buff)
                            attachment.write({
                                'datas': base64.encodestring(buff.getvalue()),
                                'datas_fname': attachment.name
                            })
                        except exceptions.AccessError:
                            _logger.info("Cannot save PDF report")
                        finally:
                            picking.ecomm_delivery_slip_loaded = True
                            buff.close()
