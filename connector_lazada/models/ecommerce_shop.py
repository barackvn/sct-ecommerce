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
                            'platform_variant_idn': u['ShopSku'],
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

    @api.model
    def _sync_orders_lazada(self, offset=0, limit=100, update_after = False):
        shops = self.env['ecommerce.shop'].search([('platform_id.platform','=','lazada')])
        for shop in shops:
            update_after = update_after or shop._last_order_sync.isoformat()
            resp = shop._py_client_lazada_request('/orders/get','GET', offset=offset, limit=limit, update_after=update_after)
            if not resp.get('data').get('count'):
                continue
            for lazada_order in resp.get('data').get('orders'):
                detail = shop._py_client_lazada_request('/order/items/get','GET', order_id = lazada_order['order_id'])
                order = self.env['sale.order'].search([
                    ('ecommerce_shop_id','=',shop.id),
                    ('client_order_ref','=',lazada_order['order_id'])
                ])[:1] or shop._new_order_lazada(lazada_order, detail=detail)
                statuses = lazada_order['statuses'].split(',')
                shop._update_order_lazada(order,statuses=statuses, detail=detail)
                shop._last_order_sync = datetime.strptime(lazada_order['updated_at'],'%Y-%m-%d %H:%M:%S %z')

    def _create_order_lazada(self, order, detail=False):
        self.ensure_one()
        detail = detail or self._py_client_lazada_request('/order/items/get','GET', order_id = order['order_id'])
        if detail['code'] != '0':
            return self._create_order_lazada(order)
        address = order['address_shipping']
        partner_id = self.env['res.partner'].search([
            ('type','!=','delivery'),
            ('phone','=',address['phone'])
        ])[:1] or self.env['res.partner'].create({
            'name': '{} {}'.format(order['customer_first_name'], order['customer_last_name']),
            'phone': address['phone'],
            })
        country_id = self.env['res.country'].search([('name','=',address['country'])])
        state_id = self.env['res.country.state'].search([('name','=',address['address3']),('country_id','=',country_id.id)])
        shipping_address = {
            'country_id': country_id.id,
            'zip': address['post_code'],
            'state_id': state_id.id,
            'city': address['address4'],
            'street2': address['address5'],
            'street': address['address1']
            }
        shipping_ids = partner_id.child_ids.filtered(lambda child: all(child.mapped(lambda c: c[field].id if isinstance(c[field],fields.Many2one) else c[field]).casefold() == val.casefold() for field, val in shipping_address.items())) 
        if shipping_ids:
            shipping_id = shipping_ids[0]
        else:
            shipping_address.update({
                'type': 'delivery',
                'parent_id': partner_id.id,
                'phone': address['phone'],
            })
            shipping_id = self.env['res.partner'].create(shipping_address)
        sale_order = self.env['sale.order'].create({
            'ecommerce_shop_id' : self.id,
            'team_id': self.team_id and self.team_id.id,
            'client_order_ref': order['order_id'],
            'partner_id': shipping_id.id,
            'order_line':[(0, _, {
                'product_id' : item['shop_sku'] and self.env['ecommerce.product.product'].search([
                    ('platform_variant_idn','=',item['shop_sku'])
                ]).product_product_id.id or self.env.ref("connector_shopee.shopee_product_product_default").id,
                'name': item['name'],
                'price_unit': item['paid_price'],
                'product_uom_qty': 1,
                    #'route_id': self.route_id.id,
                }) for item in detail['data']], 
            })
        return sale_order

    def _update_order_lazada(self, order, statuses=[], detail=False):
        for status in statuses:
            if status == 'ready_to_ship':
                if order.state == 'draft': order.action_confirm()
            elif status == 'canceled':
                order.action_cancel()
            elif status == 'delivered':
                if order.state == 'sale': order.action_done()

