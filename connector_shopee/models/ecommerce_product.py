#-*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class ShopeeProductPreset(models.Model):
    _name = 'shopee.product.preset'
    _inherit = 'ecommerce.product.preset'

    product_tmpl_ids = fields.One2many('product.template', 'shopee_product_preset_id', readonly=True)
    name = fields.Char("Name")
#    category_id = fields.Integer(related='ecomm_categ_id.platform_categ_idn', store=True, readonly=True)
#    category_name = fields.Char(string=_("Shopee Category"), related='ecomm_categ_id.complete_name', readonly=True)
    description = fields.Text(string=_("Description"))
    weight = fields.Float(string=_("Package Weight (kg)"))
    package_length = fields.Float(string=_("Package Lenghth (cm)"))
    package_width = fields.Float(string=_("Package Width (cm)"))
    package_height = fields.Float(string=_("Package Height (cm)"))
    size_chart = fields.Binary(string=_("Size Chart"))
    condition = fields.Selection(selection=[('NEW',_("New")),('USED', _("Used"))],string=_("Shopee Condition"))
    status = fields.Selection(selection=[('NORMAL',_("Normal")),('DELETED',_("Deleted")),('BANNED',_("Banned")),('UNLIST',_("Unlisted"))], string=_("Status"), readonly=True)
    is_pre_order = fields.Boolean(string=_("Is Pre-order"))
    days_to_ship = fields.Integer(string=_("Days To Ship"))

    def format_attr_values(self):
        self.ensure_one()
        return [{
            'idn': line.attr_id.platform_attr_idn,
            'value': line.value_id.name
        } for line in self.ecomm_attribute_lines] 

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

    def _sync_info_shopee(self):
        self.ensure_one()
        if not self.platform_item_idn: 
            return
        details = self.shop_id._py_client_shopee().item.get_item_detail(item_id=int(self.platform_item_idn)).get('item',{})
        if details.get('has_variation'):
            vari_details = self.shop_id._py_client_shopee().item.get_variations(item_id=int(self.platform_item_idn))
            write_attr_val = []
            attr_lines = self.attribute_line_ids
            for s, t in enumerate(vari_details['tier_variation']):
                line = attr_lines.filtered(lambda l: l.name.lower() == t['name'].lower())[:1]
                if line:
                    write_line_val = []
                    line_values = line.line_value_ids
                    for i, o in enumerate(t['options']):
                        l_value = line_values.filtered(lambda lv: lv.name.lower() == o.lower())[:1]
                        if l_value:
                            write_line_val.append((1, l_value.id, {
                                'sequence': i,
                                'ecomm_product_image_ids': [(2, img.id, 0) for img in l_value.ecomm_product_image_ids] if s else \
                                [(1, l_value.ecomm_product_image_ids[0].id, {
                                    'image_url': t.get('images_url') and t['images_url'][i] or ''
                                })] if l_value.ecomm_product_image_ids else [(0, 0, {
                                    'name': l_value.name,
                                    'res_model': 'ecommerce.product.template.attribute.line.value',
                                    'image_url': t.get('images_url') and t['images_url'][i] or ''
                                })]
                            }))
                            line_values -= l_value
                        else:
                            write_line_val.append((0, 0, {
                                'value_id': line.attr_id.value_ids.filtered(lambda v: v.name.lower() == o.lower())[:1].id,
                                'name': o,
                                'sequence': i,
                                'ecomm_product_image_ids': [(0, 0, {
                                    'name': o,
                                    'res_model': 'ecommerce.product.template.attribute.line.value',
                                    'image_url': t.get('images_url') and t['images_url'][i] or ''
                                })] if not s else False
                            }))
                    if line_values:
                        write_line_val += [(2, v.id, 0) for v in line_values]
                    write_attr_val.append((1, line.id, {
                        'sequence': s,
                        'line_value_ids': write_line_val
                    }))
                    attr_lines -= line
                else:
                    attr_id = self.env['product.attribute'].search([('create_variant','=','always'),('name','=ilike',t['name'])], limit=1)
                    write_attr_val.append((0, 0, {
                        'sequence': s,
                        'attr_id': attr_id.id,
                        'name': t['name'],
                        'line_value_ids': [(0, 0, {
                            'value_id': attr_id and attr_id.filtered(lambda v: v.name.lower() == o.lower())[:1].id,
                            'name': o,
                            'sequence': i,
                            'ecomm_product_image_ids': [(0, 0, {
                                'name': o,
                                'res_model': 'ecommerce.product.template.attribute.line.value',
                                'image_url': t.get('images_url') and t['images_url'][i] or ''
                            })] if not s else False,
                        }) for i, o in enumerate(t['options'])],
                    }))
            if attr_lines: 
                write_attr_val += [(2, l.id, 0) for l in attr_lines]
            self.write({'attribute_line_ids': write_attr_val})
            updated_vals = self.update_variant_ids().get('value')
            if updated_vals:
                self.write(updated_vals)
            #product variant updated
            for p, v in zip(self.ecomm_product_product_ids, details.get("variations", [])):
                p.write({
                    'platform_variant_idn': str(v.get('variation_id')),
                    'sku': v.get('variation_sku'),
                    'price': v.get('price'),
                })
                
        l_id = len(self.ecomm_product_image_ids)
        details['images'] += ([""]*(9-len(details.get("images",[]))))
        self.write({
            'name': details.get('name',False),
            'description': details.get('description',False),
            'sku': details.get('item_sku'),
            'price': details.get('price'),
            'ecomm_product_image_ids': [(2, img.id, 0) for img in self.ecomm_product_image_ids[9:]] + [(1, self.ecomm_product_image_ids[i].id, {
                'name': 'Cover' if i==0 else 'Image {}'.format(i),
                'sequence': i,
                'res_model': 'ecommerce.product.template',
                'image_url': url,
            }) if i < l_id else (0, _, {
                'name': 'Cover' if i==0 else 'Image {}'.format(i),
                'sequence': i,
                'res_model': 'ecommerce.product.template',
                'image_url': url,
                }) for i, url in enumerate(details['images'])],
            '_last_sync': datetime.now(),
        })
                
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
        limit.calculate_stock()
        items = [{
            'item_id': int(t.platform_item_idn),
            'stock': t.stock,
        } for t in limit]
        shop_id._py_client_shopee().item.update_stock_batch(items = items)
        if len(self) > 50: (self-limit)._update_item_stock_shopee()

    def _add_to_shop_shopee(self, data=None):
        self.ensure_one()
        preset = self.product_tmpl_id.mapped('{}_product_preset_id'.format(self.platform_id.platform))
        self.calculate_stock()
        self.ecomm_product_product_ids.calculate_stock()
        data = data or {}
        data.update({
            'category_id': preset.ecomm_categ_id.platform_categ_idn,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'item_sku': self.product_tmpl_id.default_code,
            'images': [{'url': url} for url in self._upload_image_shopee(self.mapped('ecomm_product_image_ids.image_url')) if url],
            'attributes': [{
                'attributes_id': a['idn'],
                'value': a['value']
            } for a in preset.format_attr_values()],
            'logistics': [{
                'logistic_id': l.ecomm_carrier_id.logistic_idn,
                'enabled': l.enable,
            } for l in self.carrier_ids],
            'weight': preset.weight,
            'package_length': int(preset.package_length),
            'package_width': int(preset.package_width),
            'package_height': int(preset.package_height),
            'days_to_ship': preset.days_to_ship,
            #'size_chart': preset.size_chart,
            'condition': preset.condition,
            'status': preset.status,
            'is_pre_order': preset.is_pre_order,
        })
        resp = self.shop_id._py_client_shopee().item.add({k : v for k,v in data.items() if v})
        if resp.get('item_id'):
            write_vals = {
                'platform_item_idn': resp['item_id'],
                'status': resp['item']['status'],
            }
            if self.attribute_line_ids:
                if len(self.attribute_line_ids) > 2:
                    raise exceptions.UserError('Tier variation should be under 2 level')
                tier_variation = [{
                    'name': line.name,
                    'options': line.line_value_ids.mapped('name')
                } for line in self.attribute_line_ids[:2]]
                image_urls = [val.ecomm_product_image_ids[:1].image_url for val in self.attribute_line_ids[0].line_value_ids]
                if all(image_urls):
                    tier_variation[0]['images_url'] = self._upload_image_shopee(image_urls)
                    write_vals.update({
                        'attribute_line_ids': [(1, self.attribute_line_ids[0].id, {
                            'line_value_ids': [(1, line.id, {
                                'ecomm_product_image_ids': [(1, line.ecomm_product_image_ids[0].id, {
                                    'image_url': image_urls[i],
                                })]
                            }) for i, line in enumerate(self.attribute_line_ids[0].line_value_ids)]
                        })],
                    })
                variation = []
                for v in self.ecomm_product_product_ids:
                    vals = {
                        'tier_index': v.attr_line_value_ids.mapped('sequence'),
                        'stock': v.stock,
                        'price': v.price
                    }
                    if v.sku:
                        vals['variation_sku'] = v.sku
                    variation.append(vals)
                init_data = {
                    'item_id': resp['item_id'],
                    'tier_variation': tier_variation,
                    'variation': variation,
                }
                init_resp = self.shop_id._py_client_shopee().item.init_tier_variation(**init_data)
                if init_resp.get('variation_id_list'):
                    write_vals.update({
                        'ecomm_product_product_ids': [(1, v.id, {
                            'platform_variant_idn': init_resp['variation_id_list'][i]['variation_id']
                        }) for i, v in enumerate(self.ecomm_product_product_ids)]
                    })
            self.write(write_vals)

    def _upload_image_shopee(self, image_urls):
        self.ensure_one()
        i=0
        has_urls = [[i, img] for i, img in enumerate(image_urls) if img]
        while i < len(has_urls):
            images = self.shop_id._py_client_shopee().image.upload_image(images=[img for j, img in has_urls[i:i+9]]).get('images') or []
            for j, img in enumerate(images):
                has_urls[i+j][1] = img['shopee_image_url'] 
            i+=9
        for i,url in has_urls:
            image_urls[i] = url
        return image_urls

    def _update_image_shopee(self):
        self.ensure_one()
        image_urls = self._upload_image_shopee([img.image_url for img in self.ecomm_product_image_ids if img.image_url])
        if image_urls:
            resp = self.shop_id._py_client_shopee().item.update_img(item_id=int(self.platform_item_idn), images=image_urls)
            if resp.get('images'):
                pairs = zip(self.ecomm_product_image_ids.ids, resp.get('images'))
                self.write({
                    'ecomm_product_image_ids': [(1, p[0], {
                        'image_url': p[1],
                    }) for p in pairs]
                })

    def _update_info_shopee(self, data={}):
        self.ensure_one()
        self.calculate_stock()
        self.ecomm_product_product_ids.calculate_stock()
        new_v = self.ecomm_product_product_ids.filtered(lambda r: not r.platform_variant_idn)
        o = len(self.ecomm_product_product_ids - new_v)
        if self.attribute_line_ids:
            if len(self.attribute_line_ids) > 2:
                raise exceptions.UserError('Tier variation should be under 2 level')
            tier_variation = [{
                'name': line.name,
                'options': line.line_value_ids.mapped('name')
            } for line in self.attribute_line_ids[:2]]
            tier_variation[0]['images_url'] = self._upload_image_shopee(self.attribute_line_ids[0].line_value_ids.mapped('ecomm_product_image_ids.image_url'))
            add_variant_data = [{
                'tier_index': attr_line_value_ids.mapped('sequence'),
                'stock': v.stock,
                'price': v.price,
                'variation_sku': v.sku,
            } for i, v in enumerate(new_v)]
            if o == 0:
                resp = self.shop_id._py_client_shopee().item.init_tier_variation(
                    item_id=int(self.platform_item_idn), 
                    tier_variation=tier_variation, 
                    variation=add_variant_data)
            else:
                list_resp = self.shop_id._py_client_shopee().item.update_tier_variation_list(item_id=int(self.platform_item_idn), tier_variation=tier_variation)
                resp = self.shop_id._py_client_shopee().item.add_tier_variation(item_id=int(self.platform_item_idn), variation=add_variant_data)
            if resp.get('item_id'):
                for i, v in enumerate(new_v):
                    v.platform_variant_idn = resp['variation_id_list'][i]['variation_id']
        data.update({
            'item_id':  int(self.platform_item_idn),
            'name': self.name,
            'description': self.description,
            'item_sku': self.sku or ' ',
            'price': self.price,
            'variations': [{
                'variation_id': int(v.platform_variant_idn),
                'variation_sku': v.sku,
            } for v in self.ecomm_product_product_ids]
        })
        resp = self.shop_id._py_client_shopee().item.update_item(data)
        if resp.get('item',{}).get('images') != [img.image_url for img in self.ecomm_product_image_ids if img.image_url]:
            self._update_image_shopee()
        if True:
            self._last_info_update = fields.Datetime.now()

    def _onchange_product_id_shopee(self):
        if self.platform_item_idn or self.product_product_id and self.product_tmpl_id == self.product_product_id.product_tmpl_id: return
        if self.product_tmpl_id.id != self.t_product_tmpl_id:
            self.update({
                'product_product_id': False,
                't_product_tmpl_id': self.product_tmpl_id.id,
                'ecomm_product_product_ids': [(5, _, _)]+ [(0, _, {
                    'name': ', '.join(p.mapped('attribute_value_ids.name')),
                    'product_product_id': p.id,
                    'sku': p.default_code,
                    'price': p.lst_price,
                }) for p in self.product_tmpl_id.mapped('product_variant_ids')]
            })
        elif self.product_product_id:
            self.update({
                'product_tmpl_id': self.product_product_id.product_tmpl_id.id,
                't_product_tmpl_id': self.product_product_id.product_tmpl_id.id,
                'ecomm_product_product_ids': [(5, _, _)]
            })
        elif not self.ecomm_product_product_ids and self.product_tmpl_id:
            self.update({
                'product_product_id': self.product_tmpl_id.product_variant_ids[0].id
            })
        #    self.update({'ecomm_product_product_ids': [(5, _, _)]})
            
    def _onchange_shop_id_shopee(self):
        if self.platform_item_idn: return
        if self.shop_id:
            self.carrier_ids = False
            self.update({'carrier_ids': [(0, _, {
                'ecomm_carrier_id': c.ecomm_carrier_id.id,
                'enable': True,
            }) for c in self.shop_id.carrier_ids.filtered('enable')]})
            if not self.ecomm_product_image_ids:
                self.update({
                    'ecomm_product_image_ids': [(0, 0, {
                        'res_model': 'ecommerce.product.template',
                        'name': 'Cover',
                        'sequence': 0
                    })] + [(0, 0, {
                        'res_model': 'ecommerce.product.template',
                        'name': 'Image {}'.format(i),
                        'sequence': i
                    }) for i in range(1,9)]
                })

    def _load_preset_shopee(self):
        self.ensure_one()
        preset = self.product_tmpl_id.mapped('{}_product_preset_id'.format(self.platform_id.platform))
        self.update({
            'name': preset.name,
            'description': preset.description,
            'ecomm_product_image_ids': [(0, _, {
                'name': i.name,
                'image_url': i.image_url,
                'res_id': self.id,
                'res_model': 'ecommerce.product.template'
            }) for i in preset.ecomm_product_image_ids],
        })

    def _make_preset_shopee(self, context=None, data=None):
        self.ensure_one()
        if not self.product_tmpl_id:
            raise exceptions.UserError('Can not set preset for unmatched product')
        preset_id = self.product_tmpl_id.shopee_product_preset_id or self.env['shopee.product.preset'].create({
            'platform_id': self.platform_id.id,
            'ecomm_categ_selector_id': self.env['ecommerce.category.selector'].create({
                'platform_id': self.platform_id.id,
            }).id,
            'product_tmpl_ids': [(4, self.product_tmpl_id.id, _)],
        })
        if data: 
            val = data
        elif self.platform_item_idn:
            data = self.shop_id._py_client_shopee().item.get_item_detail(item_id=int(self.platform_item_idn)).get('item')
            val = {k: data.get(k) for k in ['name', 'description', 'weight', 'package_length', 'package_width', 'package_height', 'condition', 'is_pre_order', 'days_to_ship']}
            #size_chart
            attrs = self.shop_id._py_client_shopee().item.get_attributes(category_id=data.get('category_id')).get('attributes')
            for i, attr in enumerate(attrs):
                attr['attribute_value'] = data.get('attributes')[i]['attribute_value']
                attr['attr_id'] = self.env['ecommerce.attribute'].search([
                    ('platform_id', '=', self.platform_id.id),
                    ('platform_attr_idn', '=', attr['attribute_id'])
                ])[:1].id or self.env['ecommerce.attribute'].create({
                    'name': attr['attribute_name'],
                    'platform_id': self.platform_id.id,
                    'platform_attr_idn': attr['attribute_id'],
                    'mandatory': attr['is_mandatory'],
                    'attr_type': attr['attribute_type'],
                    'input_type': attr['input_type'],
                    'value_ids': [(0,_,{
                        'name': option,
                    }) for option in attr['options']],
                }).id
            val.update({
                'platform_id': self.platform_id.id,
                'ecomm_categ_id': self.env['ecommerce.category'].search([('platform_id','=',self.platform_id.id),('platform_categ_idn','=', data.get('category_id'))])[:1].id,
                'ecomm_attribute_lines': [(0, _, {
                    'attr_id': attr['attr_id'],
                    'res_id': preset_id.id,
                    'res_model': preset_id._name,
                    'value_id': self.env['ecommerce.attribute.value'].search([('attr_id','=',attr['attr_id']),('name','=',attr['attribute_value'])])[:1].id,
                }) for attr in attrs],
                'ecomm_product_image_ids': [(0, _, {
                    'sequence': i.sequence,
                    'name': i.name,
                    'image_url': i.image_url,
                    'res_id': preset_id.id,
                    'res_model': preset_id._name,
                }) for i in self.ecomm_product_image_ids]
            })
        else:
            raise exceptions.UserError('No data to set')
        preset_id.ecomm_categ_selector_id.write({'ecomm_categ_id': val['ecomm_categ_id']})
        preset_id.write(val)

class ShopeeProductProduct(models.Model):
    _inherit = 'ecommerce.product.product'

    def _update_variation_stock_shopee(self):
        shop_id = self.mapped('ecomm_product_tmpl_id.shop_id')
        shop_id.ensure_one()
        limit = self[:50]
        limit.calculate_stock()
        variations = [{
            'item_id': int(v.ecomm_product_tmpl_id.platform_item_idn),
            'variation_id': int(v.platform_variant_idn),
            'stock': v.stock,
        } for v in limit]
        _logger.info(variations)
        shop_id._py_client_shopee().item.update_variation_stock_batch(variations = variations)
        if len(self) > 50: (self-limit)._update_variation_stock_shopee()
