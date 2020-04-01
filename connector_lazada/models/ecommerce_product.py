#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from xml.etree.ElementTree import Element, tostring


def to_xml_str(key, val, prolog=False):
    if isinstance(val, dict):
        val = ''.join((to_xml_str(k,v) for k,v in val.items()))
    elif isinstance(val,(list,tuple)):
        k = key.rstrip('s')
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
    categ_attribute_ids = fields.One2many('ecommerce.product.sample.attribute.line', 'lazada_sample_id')

class LazadaProductSampleAttributeLine(models.Model):
    _inherit = 'ecommerce.product.sample.attribute.line'

    lazada_sample_id = fields.Many2one('lazada.product.sample', string='Product Sample', ondelete='cascade', required=True)

class LazadaProductTemplate(models.Model):
    _inherit = 'ecommerce.product.template'

    def _update_stock_lazada(self):
        self.mapped('ecomm_product_product_ids')._update_variation_stock_lazada()

    def _update_info_lazada(self,data={}):
        self.ensure_one()
        data.update({
            'Attributes': {
                'name': self.name,
                'short_description': self.description,
            },
            'Skus': [{
                    'SellerSku': v.sku,
            } for v in self.ecomm_product_product_ids]
        })
        resp = self.shop_id._py_client_lazada_request('/product/update',payload=to_xml_str('Request',{'Product': data}))
        if resp['code']=='0':
            self._last_info_update = fields.Datetime.now()


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
