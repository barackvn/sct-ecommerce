#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ecommerce_shop_id = fields.Many2one(string=_('eCommerce Shop'),related='sale_id.ecommerce_shop_id', store=True)
