#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class ShopeeProductSample(models.Model):
    _name = 'shopee.product.sample'
    _inherit = 'ecommerce.product.sample'

    product_tmpl_ids = fields.One2many('product.template', 'shopee_product_sample_id', readonly=True)
    name = fields.Char("Name")
#    category_id = fields.Integer(related='ecomm_categ_id.platform_categ_idn', store=True, readonly=True)
#    category_name = fields.Char(string=_("Shopee Category"), related='ecomm_categ_id.complete_name', readonly=True)
    description = fields.Text(string=_("Description"))
    weight = fields.Float(string=_("Package Weight (g)"))
    package_length = fields.Float(string=_("Package Lenghth (cm)"))
    package_width = fields.Float(string=_("Package Width (cm)"))
    package_height = fields.Float(string=_("Package Height (cm)"))
    size_chart = fields.Binary(string=_("Size Chart"))
    condition = fields.Selection(selection=[('NEW',_("New")),('USED', _("Used"))],string=_("Shopee Condition"))
    status = fields.Selection(selection=[('NORMAL',_("Normal")),('DELETED',_("Deleted")),('BANNED',_("Banned")),('UNLIST',_("Unlisted"))], string=_("Status"), readonly=True)
    is_pre_order = fields.Boolean(string=_("Is Pre-order"))
    days_to_ship = fields.Integer(string=_("Days To Ship"))
    categ_attribute_ids = fields.One2many('ecommerce.product.sample.attribute.line', 'shopee_sample_id')

    

    #modify this if use stock delivery (logistic_id, enabled, shipping_fee, size_id, is_free)
#    shopee_logistics = fields.Many2many('shopee_logistics')

#   shopee_attributes(attribute_ids, value) -> later

#   shopee_wholesales(min, max, unit_price) > later

#   shopee_name, shopee_description, shopee_price, shopee_stock, shopee_item_sku, shopee_variations(name, stock, price, variation_sku), images(url)

                #class ProductAttribute(models.Model):
                #    _inherit = 'product.attribute'
                #
                    #should be in base client app
                        #is_ecomm_attribute = fields.Boolean("Is eCommerce Attribute")
                        #
                        #    ecomm_attr_ids = fields.One2many('ecommerce.attribute', 'product_attr_id')

                        #class ProductTemplateAttributeLine(models.Model):
                        #    _inherit = 'product.template.attribute.line'
                        #
                        #    is_ecom_attribute = fields.Boolean("Is eCommerce Attribute", readonly=True, related='attribute_id.is_ecom_attribute')

class ShopeeProductSampleAttributeLine(models.Model):
    _inherit = 'ecommerce.product.sample.attribute.line'

    shopee_sample_id = fields.Many2one('shopee.product.sample', string='Product Sample', ondelete='cascade', required=True)

class ShopeeProductTemplate(models.Model):
    _inherit = 'ecommerce.product.template'

    def _update_stock_shopee(self):
        no_variant_items = self.filtered(lambda t: not t.ecomm_product_product_ids)
        has_variant_items = self - no_variant_items
        if no_variant_items: no_variant_items._update_item_stock_shopee()
        if has_variant_items: has_variant_items.mapped('ecomm_product_product_ids')._update_variation_stock_shopee()

    def _update_item_stock_shopee(self):
        if self.mapped('ecomm_product_product_ids'): return
        shop_id = self.mapped('shop_id')
        shop_id.ensure_one()
        limit = self[:50]
        items = [{
            'item_id': int(t.platform_item_idn),
            'stock': int(t.product_product_id.virtual_available) if (t.product_tmpl_id.type == 'product' and t.product_tmpl_id.inventory_availability not in [False, 'never']) else 1000,
        } for t in limit]
        shop_id._py_client_shopee().item.update_stock_batch(items = items)
        if len(self) > 50: (self-limit)._update_item_stock_shopee()

    def _update_info_shopee(self, data={}):
        self.ensure_one()
        data.update({
            'item_id':  int(self.platform_item_idn),
            'name': self.name,
            'description': self.description,
            })
        resp = self.shop_id._py_client_shopee().item.update_item(data)
        if True:
            self._last_info_update = fields.Datetime.now()



class ShopeeProductProduct(models.Model):
    _inherit = 'ecommerce.product.product'

    def _update_variantion_stock_shopee(self):
        shop_id = self.mapped('ecomm_product_tmpl_id.shop_id')
        shop_id.ensure_one()
        limit = self[:50]
        variations = [{
            'item_id': int(v.ecomm_product_tmpl_id.platform_item_idn),
            'variation_id': int(v.platform_variant_idn),
            'stock': int(v.product_product_id.virtual_available) if (v.product_product_id.product_tmpl_id.type == 'product' and v.product_product_id.product_tmpl_id.inventory_availability not in [False, 'never']) else 1000,
        } for v in limit]
        shop_id._py_client_shopee().item.update_variation_stock_batch(variations = variations)
        if len(self) > 50: (self-limit)._update_variantion_stock_shopee()
