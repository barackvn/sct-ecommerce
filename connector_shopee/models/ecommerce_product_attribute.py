# -*- coding: utf-8 -*-

from odoo import api, fields, models

class eCommerceProductTemplateAttributeLineValue(models.Model):
    _inherit = 'ecommerce.product.template.attribute.line.value'

    def _onchange_name_shopee(self):
        if self.sequence == 0 and self.name and not self.ecomm_product_image_ids:
            self.update({
                'ecomm_product_image_ids': [(0, 0, {
                    'res_model': 'ecommerce.product.template.attribute.line.value',
                    'name': self.name,
                })]*1
            })
