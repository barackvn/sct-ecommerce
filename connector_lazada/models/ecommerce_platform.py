# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class eCommercePlatform(models.Model):
    _inherit = 'ecommerce.platform'

    platform = fields.Selection(selection_add=[('lazada','Lazada')])


