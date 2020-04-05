# -*- coding: utf-8 -*-
#create for structure purpose, not in use, might be use in future updates
from odoo import fields, models, api, _
import pyshopee

class eCommercePlatform(models.Model):
    _inherit = 'ecommerce.platform'

    platform = fields.Selection(selection_add=[('shopee','Shopee')])

    def _py_client_shopee(self):
        self.ensure_one()
        return pyshopee.Client(False, self.partner_id, self.key)
