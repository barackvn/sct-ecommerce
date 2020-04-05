#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from xml.etree.ElementTree import Element, tostring


def to_xml_str(key, val, prolog=False):
    if isinstance(val, dict):
        val = ''.join((to_xml_str(k,v) for k,v in val.items()))
    elif isinstance(val,(list,tuple)):
        k = key[:-1]
        val = ''.join((to_xml_str(k,v) for v in val))
    return '{prolog}<{key}>{val}</{key}>'.format(prolog='{}'.format(prolog and '<?xml version="1.0" encoding="UTF-8"?>' or ''),key=key,val=val)

class LazadaProductSample(models.Model):
    _name = 'lazada.product.sample'
    _inherit = 'ecommerce.product.sample'

    product_tmpl_ids = fields.One2many('product.template', 'lazada_product_sample_id', readonly=True)
    short_description = fields.Html()
    warranty_type = fields.Char(string=_("Warranty Type"))
    warranty = fields.Char(string=_("Warranty Period"))
    product_warranty = fields.Char(string=_("Warranty Policy"))
    package_weight = fields.Float(string=_("Package Weight (kg)"))
    package_length = fields.Float(string=_("Package Lenghth (cm)"))
    package_width = fields.Float(string=_("Package Width (cm)"))
    package_height = fields.Float(string=_("Package Height (cm)"))
    package_content = fields.Char(string=_("What's in the box"))
    Hazmat = fields.Char(string=_("Hazmat"))
    video = fields.Char(string=_("Video URL"))


class LazadaProductTemplate(models.Model):
    _inherit = 'ecommerce.product.template'

    def _update_stock_lazada(self):
        self.mapped('ecomm_product_product_ids')._update_variation_stock_lazada()
    
    def _add_to_shop_lazada(self):
        self.ensure_one()
        image_urls = self._upload_image_lazada(self.mapped('ecomm_product_image_ids.image_url'))
        return

    def _upload_image_lazada(self, image_urls):
        self.ensure_one()
        url_payload = to_xml_str('Urls', image_urls)
        batch = self.shop_id._py_client_lazada_request('/images/migrate', payload=to_xml_str('Request',{'Images': url_payload})).get('batch_id')
        images = self.shop_id._py_client_lazada_request('/image/response/get','GET', batch_id=batch).get('data').get('images')
        return [i['url'] for i in images]

    def _update_image_lazada(self):
        self.ensure_one()
        image_urls = self._upload_image_lazada(self.mapped('ecomm_product_image_ids.image_url'))
        if len(image_urls) == len(self.ecomm_product_image_ids):
            self.shop_id._py_client_lazada_request('/images/set', payload=to_xml_str('Request',{
                'Product': {
                    'Skus': [{
                        'SellerSku': v.sku,
                        'Images': image_urls,
                    } for v in self.ecomm_product_product_ids]
                }    
            }))
            pairs = zip(self.ecomm_product_image_ids.id, image_urls)
            self.write({
                'ecomm_product_image_ids': [(1, p[0], {
                    'image_url': p[1],
                }) for p in pairs]
            })

    def _update_info_lazada(self,vals={}):
        self.ensure_one()
        vals.update({
            'Attributes': {
                'name': self.name,
                'short_description': self.description,
            },
            'Skus': [{
                    'SellerSku': v.sku,
            } for v in self.ecomm_product_product_ids]
        })
        resp = self.shop_id._py_client_lazada_request('/product/update',payload=to_xml_str('Request',{'Product': vals}))
        if resp['code']=='0':
            self._last_info_update = fields.Datetime.now()

    def _onchange_product_id_lazada(self):
        if self.platform_item_idn: return
        if self.product_tmpl_id:
            self.update({
                'ecomm_product_product_ids': [(3, e.id, _) for e in self._origin.ecomm_product_product_ids]+ [(0, _, {
                    #'name': ', '.join(p.mapped('attribute_value_ids.name')),
                    'product_product_id': p.id,
                    'sku': p.default_code,
                }) for p in self.product_tmpl_id.product_variant_ids]
            })
        else:
            self.update({'ecomm_product_product_ids': [(3, e.id, _) for e in self._origin.ecomm_product_product_ids]})

    def _onchange_shop_id_lazada(self):
        return

class LazadaProductProduct(models.Model):
    _inherit = 'ecommerce.product.product'

    def _update_variation_stock_lazada(self):
        shop_id = self.mapped('ecomm_product_tmpl_id.shop_id')
        shop_id.ensure_one()
        limit = self[:50]
        data = [{
            'SellerSku': v.product_product_id.default_code,
            'Quantity': int(v.product_product_id.virtual_available) if (v.product_product_id.product_tmpl_id.type == 'product' and v.product_product_id.product_tmpl_id.inventory_availability not in [False, 'never']) else 1000,
        } for v in limit]
        shop_id._py_client_lazada_request('/product/price_quantity/update',payload=to_xml_str('Request',{'Product': {'Skus':data}}))
        if len(self) > 50: (self-limit)._update_variation_stock_lazada()
