#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class eCommerceShop(models.Model):
    _inherit = 'ecommerce.shop'

    def get_logistic(self):
        for shop in self:
            getattr(shop,'_get_logistic_{}'.format(shop.platform_id.platform))()

