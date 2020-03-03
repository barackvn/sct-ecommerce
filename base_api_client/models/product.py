# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    client_product_template_ids = fields.One2many('
