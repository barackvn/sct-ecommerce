# -*- coding: utf-8 -*-
#create for structure purpose, not in use, might be use in future updates
from odoo import fields, models, api, _

class eCommercePlatform(models.Model):
    _name = 'ecommerce.platform'

    name = fields.Char()
    platform = fields.Selection([])
    partner_id = fields.Integer()
    key = fields.Char()


