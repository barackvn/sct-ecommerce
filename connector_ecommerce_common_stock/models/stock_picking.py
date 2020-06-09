#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ecommerce_shop_id = fields.Many2one(string=_('eCommerce Shop'),related='sale_id.ecommerce_shop_id', store=True)
    ecomm_delivery_slip_loaded = fields.Boolean("Delivery Slip Loaded?")

    def sync_tracking_info(self): 
        dct = {}
        for p in self:
            if not p.ecommerce_shop_id:
                continue
            if dct.get(p.ecommerce_shop_id):
                dct[p.ecommerce_shop_id] |= p
            else:
                dct[p.ecommerce_shop_id] = p
        for shop, pickings in dct.items():
            getattr(pickings, '_sync_tracking_info_{}'.format(shop.platform_id.platform))(shop)
