#-*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import base64, io, requests
from PyPDF2 import PdfFileWriter, PdfFileReader
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def _sync_tracking_info_shopee(self, shop):
        report = self.env['ir.actions.report']._get_report_from_name('stock.report_deliveryslip')
        pickings_dict = {}
        for p in self:
            if pickings_dict.get(p.sale_id.client_order_ref):
                pickings_dict[p.sale_id.client_order_ref] |= p
            else:
                pickings_dict[p.sale_id.client_order_ref] = p
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
                if attachment := report.retrieve_attachment(picking):
                    streams = [io.BytesIO(base64.decodestring(attachment.datas)), io.BytesIO(requests.get(o['airway_bill']).content)]
                    writer = PdfFileWriter()
                    for stream in streams:
                        writer.appendPagesFromReader(PdfFileReader(stream))
                    if writer.getNumPages()%2==1:
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
                        picking.ecomm_delivery_slip_loaded = True
                        for stream in streams:
                            try:
                                stream.close()
                            except Exception:
                                pass
