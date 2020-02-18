# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    process_datetime = fields.Datetime(string=_("Processing Datetime"))
