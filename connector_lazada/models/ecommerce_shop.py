#-*- coding: utf-8 -*-

from odoo import api, fields, models, _
import requests, logging, lazop
from datetime import datetime
_logger = logging.getLogger(__name__)

class eCommerceShop(models.Model):
    _inherit = 'ecommerce.shop'

    #region = fields.Selection([])
    url = fields.Char('URL endpoint', help="Region url endpoint used for lazop")
    access_token = fields.Char()
    refresh_token = fields.Char()
    refresh_expires_in = fields.Float()
    account = fields.Char()


    def _py_client_lazada_request(self, *args, **kwargs):
        self.ensure_one()
        url = 'https://auth.lazada.com/rest' if ('/auth/token/create' in args or '/auth/token/refresh' in args) else self.url
        client = lazop.LazopClient(url, self.platform_id.partner_id, self.platform_id.key)
        request = lazop.LazopRequest(*args)
        for k,v in kwargs.items():
            request.add_api_param(k,v)
        response = client.execute(request, self.access_token or None)
        #_logger.info(response.__dict__)
        return response.body
    
    def _get_info_lazada(self):
        self.ensure_one()
        data = self._py_client_lazada_request('/seller/get','GET').get('data')
        if data: self.write({
            'ecomm_shop_name': data.get('name'),
            'ecomm_shop_idn': data.get('seller_id')
            })

        

    def _auth_lazada(self):
        params = {
            'client_id': self.platform_id.partner_id,
            'redirect_uri': 'https://nutishop.scaleup.top/connector_ecommerce/{}/auth'.format(self.id),
            'response_type': 'code',
            'force_auth': True
            }
        return {
            'type': 'ir.actions.act_url',
            'url' : requests.Request('GET', 'https://auth.lazada.com/oauth/authorize', params=params).prepare().url,
            'target': 'new'
            }

    def _deauth_lazada(self):
        pass

    def _get_categories_lazada(self):
        self.ensure_one()
        categs = self._py_client_lazada_request('/category/tree/get','GET').get('data')
        def _create_categ(categ, parent_id, parent_idn):
            categ_id = self.env['ecommerce.category'].create({
                'platform_id': self.platform_id.id,
                'parent_id': parent_id,
                'platform_categ_idn': categ['category_id'],
                'platform_parent_categ_idn': parent_idn,
                'name': categ['name'],
                }).id
            if categ.get('children'):
                for child in categ.get('children'):
                    _create_categ(child, categ_id, categ['category_id'])
        for categ in categs:
            _create_categ(categ, False, 0)

    def _sync_product_sku_match_lazada(self, offset=0, limit=100, update_after = False):
        self.ensure_one()
        attrs = ['name','short_description','warranty_type','warranty','product_warranty','video','Hazmat']
        sku_attrs = ['package_weight','package_length','package_width','package_height','package_content']
        update_after = update_after or self._last_sku_sync.isoformat()
        data = self._py_client_lazada_request('/products/get','GET', filter='all', update_after = update_after, offset=offset, limit=limit).get('data',{})
        if not data.get('total_products'): return
        for product in data.get('products'):
            item_idn = str(product.get('item_id',0))
            tmpls = self.env['product.template'].search([
                ('product_variant_ids.default_code','in',[u.get("SellerSku",False)]) for u in product.get("skus",[])
            ])
            for tmpl in tmpls:
                if item_idn not in tmpl.lazada_product_tmpl_ids.mapped('platform_item_idn'):
                    self.env['ecommerce.product.template'].create({
                        'name': product['attributes']['name'],
                        'description': product['attributes']['short_description'],
                        'shop_id': self.id,
                        'platform_item_idn': item_idn,
                        'product_tmpl_id': tmpl.id,
                        'ecomm_product_product_ids': [(0, _, {
                            'name': u['ShopSku'],
                            'platform_variant_idn': str(u['SkuId']),
                            'product_product_id': tmpl.product_variant_ids.filtered(lambda r: r.default_code == u.get('SellerSku'))[:1].id,
                        }) for u in product['skus']],
                    })
                    if not tmpl.lazada_product_sample_id:
                        vals = {
                            'platform_id': self.platform_id.id,
                            'ecomm_categ_id': self.env['ecommerce.category'].search([
                                ('platform_id','=',self.platform_id.id),
                                ('platform_categ_idn','=',product.get('primary_category'))
                            ]).id,
                            'product_tmpl_id': tmpl.id,
                            }
                        vals.update({a: product['attributes'].get(a) for a in attrs})
                        vals.update({s: product['skus'][0].get(s) for s in sku_attrs})
                        self.env['lazada.product.sample'].create(vals)

            if data['total_products'] > offset+limit:
                self._sync_product_sku_match_lazada(offset=offset+limit, limit=limit, update_after = update_after)
        self._last_sku_sync = fields.Datetime.now()

