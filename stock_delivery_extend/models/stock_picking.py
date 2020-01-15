# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    barcode = fields.Char()
