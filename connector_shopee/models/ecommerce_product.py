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

    

    #modify this if use stock delivery (logistic_id, enabled, shipping_fee, size_id, is_free)
#   shopee_wholesales(min, max, unit_price) > later

#   shopee_name, shopee_description, shopee_price, shopee_stock, shopee_item_sku, shopee_variations(name, stock, price, variation_sku), images(url)

    def _onchange_ecomm_categ_id_shopee(self):
        shop = self.env['ecommerce.shop'].search([('platform_id.platform','=','shopee')])[:1]
        shop.ensure_one()
        attrs = shop._py_client_shopee().item.get_attributes(category_id=self.ecomm_categ_id.platform_categ_idn).get('attributes')
        triplets = [(5, _, _)]
        for attr in attrs:
            ecomm_attrs = self.env['ecommerce.attribute'].search([
                ('platform_id', '=', self.platform_id.id),
                ('platform_attr_idn', '=', attr['attribute_id'])
            ])
            ecomm_attr = ecomm_attrs and ecomm_attrs[0] or self.env['ecommerce.attribute'].create({
                'name': attr['attribute_name'],
                'platform_id': self.platform_id.id,
                'platform_attr_idn': attr['attribute_id'],
                'mandatory': attr['is_mandatory'],
                'attr_type': attr['attribute_type'],
                'input_type': attr['input_type'],
                'value_ids': [(0,_,{
                    'name': option,
                }) for option in attr['options']],
            })
            triplets += [(0, _, {
                'attr_id': ecomm_attr.id,
                'res_id': self.id,
                'res_model': self._name
            })]
        self.update({'ecomm_attribute_lines': triplets})
        _logger.info(self.ecomm_attribute_lines.mapped('res_model'))

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
            'stock': int(t.product_product_id.virtual_available > 0 and t.product_product_id.virtual_available or 0) if (t.product_tmpl_id.type == 'product' or (t.product_product_id.pack_ok == True and 'product' in t.product_product_id.mapped('pack_line_ids.product_id.type')) and t.product_tmpl_id.inventory_availability not in [False, 'never']) else 1000,
        } for t in limit]
        shop_id._py_client_shopee().item.update_stock_batch(items = items)
        if len(self) > 50: (self-limit)._update_item_stock_shopee()

    def _add_to_shop_shopee(self, vals={}):
        self.ensure_one()
        images = self.shop_id._py_client_shopee().image.upload_image(images=self.mapped('ecomm_product_image_ids.image_url')).get('images')
        sample = self.product_tmpl_id.mapped('{}_product_sample_id'.format(self.platform_id.platform))
        vals.update({
            'category_id': sample.ecomm_categ_id.platform_categ_idn,
            'name': self.name,
            'description': self.description,
            'price': self.product_product_id and self.product_product_id.lst_price,
            'stock': self.product_product_id and (int(self.product_product_id.virtual_available > 0 and self.product_product_id.virtual_available or 0) if (self.product_tmpl_id.type == 'product' or (self.product_product_id.pack_ok == True and 'product' in self.product_product_id.mapped('pack_line_ids.product_id.type')) and self.product_tmpl_id.inventory_availability not in [False, 'never']) else 1000),
            'item_sku': self.product_tmpl_id.default_code,
            'variations': [{
                'name': v.name,
                'stock': int(v.product_product_id.virtual_available > 0 and v.product_product_id.virtual_available or 0) if (v.product_product_id.product_tmpl_id.type == 'product' or (v.product_product_id.pack_ok == True and 'product' in v.product_product_id.mapped('pack_line_ids.product_id.type')) and v.product_product_id.product_tmpl_id.inventory_availability not in [False, 'never']) else 1000,
                'price': v.product_product_id.lst_price,
                'variation_sku': v.sku,
            } for v in self.ecomm_product_product_ids],
            'images': self._upload_image_shopee(self.mapped('ecomm_product_image_ids.image_url')),
            'attributes': [{
                'attributes_id': a['idn'],
                'value': a['value']
            } for a in sample._format_attr_values_shopee()],
            'logistics': [{
                'logistic_id': l.ecomm_carrier_id.logistic_idn,
                'enabled': l.enable,
            } for l in self.carrier_ids],
            'weight': sample.weight,
            'package_length': sample.package_length,
            'package_width': sample.package_width,
            'package_height': sample.package_height,
            'days_to_ship': sample.days_to_ship,
            #'size_chart': sample.size_chart,
            'condition': sample.condition,
            'status': sample.status,
            'is_pre_order': sample.is_pre_order,
        })

    def _format_attr_values_shopee(self):
        self.ensure_one()
        return [{
            'idn': line.attr_id.platform_attr_idn,
            'value': line.value_id.name
        } for line in self.ecomm_attribute_lines]

    def _upload_image_shopee(self, image_urls):
        self.ensure_one()
        images = self.shop_id._py_client_shopee().image.upload_image(image_urls).get('images')
        return [i['shopee_image_url'] for i in images]

    def _update_image_shopee(self):
        self.ensure_one()
        image_urls = self._upload_image_shopee(self.mapped('ecomm_product_image_ids.image_url'))
        if image_urls:
            resp = self.shop_id._py_client_shopee().item.update_img(item_id=int(self.platform_item_idn), images=image_urls)
            pairs = zip(self.ecomm_product_image_ids.id, resp.get('images'))
            self.write({
                'ecomm_product_image_ids': [(1, p[0], {
                    'image_url': p[1],
                }) for p in pairs]
            })

    def _update_info_shopee(self, vals={}):
        self.ensure_one()
        vals.update({
            'item_id':  int(self.platform_item_idn),
            'name': self.name,
            'description': self.description,
            'sku': self.sku or ' ',
            'variations': [{
                'variation_id': int(v.platform_variant_idn),
                'name': v.name,
                'variation_sku': v.sku or ' ' 
            } for v in self.ecomm_product_product_ids]
        })
        resp = self.shop_id._py_client_shopee().item.update_item(vals)
        if True:
            self._last_info_update = fields.Datetime.now()

    def _onchange_product_id_shopee(self):
        if self.platform_item_idn: return
        if self.product_product_id:
            self.update({
                'product_tmpl_id': self.product_product_id.product_tmpl_id,
                'ecomm_product_product_ids': [(3, e.id, _) for e in self._origin.ecomm_product_product_ids]+ [(0, _, {
                    'name': ', '.join(self.product_product_id.mapped('attribute_value_ids.name')),
                    'product_product_id': self.product_product_id.id,
                    'sku': self.product_product_id.default_code
                })]
            })

        elif self.product_tmpl_id:
            self.update({
                'ecomm_product_product_ids': [(3, e.id, _) for e in self._origin.ecomm_product_product_ids]+ [(0, _, {
                    'name': ', '.join(p.mapped('attribute_value_ids.name')),
                    'product_product_id': p.id,
                    'sku': p.default_code,
                }) for p in self.product_tmpl_id.product_variant_ids]
            })
        else: 
            self.update({'ecomm_product_product_ids': [(3, e.id, _) for e in self._origin.ecomm_product_product_ids]})
            
    def _onchange_shop_id_shopee(self):
        if self.platform_item_idn: return
        if self.shop_id:
            self.update({'carrier_ids': [(3, o.id, _) for o in self._origin.carrier_ids] + [(0, _, {
                'ecomm_carrier_id': c.id,
                'enable': True,
            }) for c in self.shop_id.carrier_ids.filtered('enable')]})

class ShopeeProductProduct(models.Model):
    _inherit = 'ecommerce.product.product'

    def _update_variation_stock_shopee(self):
        shop_id = self.mapped('ecomm_product_tmpl_id.shop_id')
        shop_id.ensure_one()
        limit = self[:50]
        variations = [{
            'item_id': int(v.ecomm_product_tmpl_id.platform_item_idn),
            'variation_id': int(v.platform_variant_idn),
            'stock': int(v.product_product_id.virtual_available > 0 and v.product_product_id.virtual_available or 0) if (v.product_product_id.product_tmpl_id.type == 'product' or (v.product_product_id.pack_ok == True and 'product' in v.product_product_id.mapped('pack_line_ids.product_id.type')) and v.product_product_id.product_tmpl_id.inventory_availability not in [False, 'never']) else 1000,
        } for v in limit]
        shop_id._py_client_shopee().item.update_variation_stock_batch(variations = variations)
        if len(self) > 50: (self-limit)._update_variation_stock_shopee()
