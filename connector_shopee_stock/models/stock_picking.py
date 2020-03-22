#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _sync_tracking_ref_shopee(self):
        for p in self:
            order = p.sale_id
            logistic = order.ecommerce_shop_id and order.ecommerce_shop_id._py_client_shopee().logistic.get_order_logistic(ordersn=order.client_order_ref).get('logistics')
            if logistic:
                p.carrier_id = self.env['ecommerce.carrier'].search([
                    ('logistic_idn', '=', logistic.get('logistic_id'))
                    ])[:1].carrier_id
                p.carrier_tracking_ref = logistic.get('tracking_no')
