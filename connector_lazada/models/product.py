#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lazada_product_sample_id = fields.Many2one('lazada.product.sample')
    lazada_product_tmpl_ids = fields.One2many('ecommerce.product.template','product_tmpl_id', string="Lazada Products", domain=[('platform_id.platform','=','lazada')])
