#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopee_product_sample_id = fields.Many2one('shopee.product.sample')
    shopee_product_tmpl_ids = fields.One2many('ecommerce.product.template','product_tmpl_id', compute='_compute_shopee_product_tmpl_ids', store=True)

    @api.depends('ecomm_product_tmpl_ids')
    def _compute_shopee_product_tmpl_ids(self):
        for tmpl in self:
            tmpl.shopee_product_tmpl_ids = tmpl.ecomm_product_tmpl_ids.filtered(lambda r: r.platf_id.platform == 'shopee')
