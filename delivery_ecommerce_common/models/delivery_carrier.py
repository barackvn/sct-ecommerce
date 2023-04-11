#-*- coding: UTF-8 -*-

from odoo import models, api, fields

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('ecommerce_jtexpress','eCommerce J&T Express'),
        ('ecommerce_giaohangtietkiem', 'eCommerce Giaohangtietkiem'),
        ('ecommerce_spx','eCommerce Shopee Express'),
        ('ecommerce_lex','eCommerce LEX'),
        ('ecommerce_ninjavan','eCommerce Ninja Van'),
        ('ecommerce_vncpost','eCommerce Vinacapital Post')
    ])

    def ecommerce_jtexpress_get_tracking_link(self, picking):
        return f"https://jtexpress.vn/vn/express/track?billcodes={picking.carrier_tracking_ref}"
    
    def ecommerce_giaohangtietkiem_get_tracking_link(self, picking):
        return "https://giaohangtietkiem.vn/#searchPrice"

    def ecommerce_spx_get_tracking_link(self, picking):
        return f"https://spx.vn/#/detail/{picking.carrier_tracking_ref}"

    def ecommerce_lex_get_tracking_link(self, picking):
        return f"https://tracker.lel.asia/tracker?trackingNumber={picking.carrier_tracking_ref}"

    def ecommerce_ninjavan_get_tracking_link(self, picking):
        return f"https://www.ninjavan.co/en-vn/tracking?id={picking.carrier_tracking_ref}"

    def ecommerce_vncpost_get_tracking_link(self, picking):
        return f"https://vncpost.com/hanh-trinh-don-hang?code={picking.carrier_tracking_ref}"


