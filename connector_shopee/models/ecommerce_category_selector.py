#-*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)

class eCommercerCategorySelector(models.Model):
    _inherit = 'ecommerce.category.selector'


    def _action_create_preset_shopee(self, ctx):
        return {
            "type": "ir.actions.act_window",
            "res_model": "shopee.product.preset",
            "views": [[self.env.ref("connector_shopee.shopee_product_preset_form_view").id, "form"]],
            "target": "current",
            "context": ctx
        } 
