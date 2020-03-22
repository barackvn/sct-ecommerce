#-*- coding: utf-8 -*-

from odoo import fields, models, api, _

class eCommerceProductPreview(models.TransientModel):
    _name = 'ecommerce.product.preview'

    name = fields.Char(readonly="1")
    description = fields.Text(readonly="1")
