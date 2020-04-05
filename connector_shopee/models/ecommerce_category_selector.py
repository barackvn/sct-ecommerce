#-*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)

class eCommercerCategorySelector(models.Model):
    _inherit = 'ecommerce.category.selector'


    def _action_create_sample_shopee(self):
        ctx = self._context
        ctx.update({"default_ecomm_categ_selector_id": self.id})
        return {
                "type": "ir.actions.act_window",
                "res_model": "shopee.product.sample",
                "views": [[self.env.ref("connector_shopee.shopee_product_sample_form_view").id, "form"]],
                "target": "current",
                "context": ctx,
               } 
