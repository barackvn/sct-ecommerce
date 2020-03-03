# -*- coding: utf-8 -*-
#create for structure purpose, not in use, might be use in future updates
from odoo import fields, models, api, _

class eCommercePlatform(models.Model):
    _inherit = 'ecommerce.platform'

    platform = fields.Selection(selection_add=[('shopee','Shopee')])


