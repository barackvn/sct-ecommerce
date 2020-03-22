#-*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)

class eCommercerCategorySelector(models.TransientModel):
    _inherit = 'ecommerce.category.selector'


    def _action_create_sample_shopee(self):
        product_template = self.env['product.template'].browse(self._context.get("active_id"))
        return {
                "type": "ir.actions.act_window",
                "res_model": "shopee.product.sample",
                "views": [[self.env.ref("shopee_ecommerce_client.shopee_product_sample_form_view").id, "form"]],
                "target": "current",
                "context": {
                    "default_name": product_template.name,
                    "default_desciption": product_template.website_description or product_template.description,
                    "default_ecomm_categ_id": self._context.get("ecomm_categ_id")
                    }
               } 
