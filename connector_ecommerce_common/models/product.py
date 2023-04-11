# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

#    shopee_sale_ok = fields.Boolean(string=_("Can be Sold with Shopee"), default=True)
    ecomm_product_preset_id = fields.Many2one('ecommerce.product.preset')
    ecomm_product_tmpl_ids = fields.One2many('ecommerce.product.template', 'product_tmpl_id')
#    ecomm_categ_id = fields.Many2one('ecommerce.category')
#    shopee_category_name = fields.Char(string=_("Shopee Category"), related='shopee_client_category_id.complete_name', readonly=True)
#    shopee_package_weight = fields.Float(string=_("Shopee Package Weight (g)"))
#    shopee_package_length = fields.Float(string=_("Shopee Package Lenghth (cm)"))
#    shopee_package_width = fields.Float(string=_("Shopee Package Width (cm)"))
#    shopee_package_height = fields.Float(string=_("Shopee Package Height (cm)"))
#    shopee_size_chart = fields.Binary(string=_("Shopee Size Chart"))
#    shopee_condition = fields.Selection(selection=[('new',_("New")),('used', _("Used"))],string=_("Shopee Condition"))
#    shopee_status = fields.Selection(selection=[('normal',_("Normal")),('unlist',_("Unlisted"))], string="Shopee Status")
#    shopee_is_pre_order = fields.Boolean(string=_("Shopee Is Pre-order"))
#    shopee_days_to_ship = fields.Integer(string=_("Shopee Days To Ship"))

    #modify this if use stock delivery (logistic_id, enabled, shipping_fee, size_id, is_free)
#    shopee_logistics = fields.Many2many('shopee_logistics')

    #shopee_attributes(attribute_ids, value) -> later

    #shopee_wholesales(min, max, unit_price) > later

    #shopee_name, shopee_description, shopee_price, shopee_stock, shopee_item_sku, shopee_variations(name, stock, price, variation_sku), images(url)

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

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_virtual_expire(self, field=False):
        self.ensure_one()
        if (
            lots := self.env['stock.quant']
            .search(
                [
                    ('product_id', '=', self.id),
                    ('location_id.usage', '=', 'internal'),
                ]
            )
            .filtered(lambda q: q.reserved_quantity < q.quantity)
            .mapped('lot_id')
            .sorted(field or 'name')
        ):
            return lots[0][field or 'name']
        else:
            return False

