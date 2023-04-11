#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class eCommerceShop(models.Model):
    _inherit = 'ecommerce.shop'

    def get_logistic(self):
        for shop in self:
            getattr(shop, f'_get_logistic_{shop.platform_id.platform}')()

