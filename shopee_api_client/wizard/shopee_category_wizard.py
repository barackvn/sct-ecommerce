# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ShopeeClientCategoryWizard(models.TransientModel):
    _name = 'shopee_client.category.wizard'

    tier1 = fields.Many2one('shopee_client.category')
    tier2 = fields.Many2one('shopee_client.category')
    tier3 = fields.Many2one('shopee_client.category')
    complete_name = fields.Char(readonly=True)
