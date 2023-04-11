#-*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import base64, io, requests
from PyPDF2 import PdfFileWriter, PdfFileReader
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def _sync_tracking_info_lazada(self,shop):
        report = self.env['ir.actions.report']._get_report_from_name('stock.report_deliveryslip')
        pickings_dict = {}
        for p in self:
            if pickings_dict.get(p.sale_id.client_order_ref):
                pickings_dict[p.sale_id.client_order_ref] |= p
            else:
                pickings_dict[p.sale_id.client_order_ref] = p
        ordersn_list = list(pickings_dict.keys())
        details_list = shop._py_client_lazada_request('/orders/items/get', 'GET', order_ids=str(ordersn_list)).get('data')
        to_update_pairs = [(d, d['order_items'][0]['order_item_id']) for d in details_list if d['order_items'][0].get('tracking_code')]
        orders_detail, order_item_ids = zip(*to_update_pairs)
        resp = shop._py_client_lazada_request('/order/document/get', 'GET', doc_type='shippingLabel', order_item_ids=str(list(order_item_ids)))
        if not resp.get('data'):
            return
        raw = resp['data']['document']['file']
        Report = self.env['ir.actions.report']
        doc_stream = io.BytesIO(Report._run_wkhtmltopdf([base64.b64decode(raw)]))
        streams = [doc_stream]
        pdf_doc = PdfFileReader(doc_stream)
        for page in range(pdf_doc.getNumPages()):
            detail = orders_detail[page]
            pickings = pickings_dict[str(detail['order_id'])]
            vals = {
                'carrier_tracking_ref': detail['order_items'][0]['tracking_code'],
                'carrier_id': self.env['ecommerce.carrier'].search([
                    ('platform_id','=',shop.platform_id.id),
                    ('name','=', detail['order_items'][0]['shipment_provider'].split('Delivery: ')[-1]),
                ])[:1].carrier_id.id,
            }
            pickings.write(vals)
            for picking in pickings:
                if picking.ecomm_delivery_slip_loaded:
                    continue
                report.render(picking.ids)
                if attachment := report.retrieve_attachment(picking):
                    stream = io.BytesIO(base64.decodestring(attachment.datas))
                    writer = PdfFileWriter()
                    writer.appendPagesFromReader(PdfFileReader(stream))
                    writer.addPage(pdf_doc.getPage(page))
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
                        picking.ecomm_delivery_slip_loaded = True
        for stream in streams:
            try:
                stream.close()
            except Exception:
                pass

