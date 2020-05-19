# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import requests, logging
from odoo.addons.connector_shopee import pyshopee
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class eCommercerShop(models.Model):
    _inherit = 'ecommerce.shop'

    def _auth_shopee(self):
        self.ensure_one()
#        client_name = self._cr.dbname
        redirect_url = "{}/connector_ecommerce/{}/auth".format(self.env['ir.config_parameter'].sudo().get_param('web.base.url'),self.id)
#        req = requests.post(url=url, data={'client':client_name,'client_shop_id': self.id, 'name': self.name})
        return {
            "type": "ir.actions.act_url",
            "url": self._py_client_shopee().shop.authorize(redirect_url=redirect_url),
            "target": "new",
        }

    def _deauth_shopee(self):
        self.ensure_one()
        redirect_url = "{}/connector_ecommerce/{}/auth".format(self.env['ir.config_parameter'].sudo().get_param('web.base.url'),self.id)
        return {
            "type": "ir.actions.act_url",
            "url": self._py_client_shopee().shop.cancel_authorize(redirect_url=redirect_url),
            "target": "new",
        }

    def _get_info_shopee(self):
        self.ensure_one()
        resp = self._py_client_shopee().shop.get_shop_info()
        self.write({
            'ecomm_shop_name': resp.get('shop_name')
            })
        if not self.name: self.name = self.ecomm_shop_name

    def _py_client_shopee(self, platform=False):
        self.ensure_one()
        return pyshopee.Client(self.ecomm_shop_idn, self.platform_id.partner_id, self.platform_id.key)

    def _get_categories_shopee(self):
        categs = self._py_client_shopee().item.get_categories().get('categories')
        path = [(False,0)] # categ (id,idn)
        rec = None
        need_prnt = []
        for categ in categs:
            if self.env['ecommerce.category'].search([('platform_id','=', self.platform_id.id),('platform_categ_idn','=',categ['category_id'])]):
                continue
            temp = path[:]
            while path and path[-1][1] != categ['parent_id']: 
                path.pop()
            if not path:
                path = temp[:]
                temp_parent = self.env['ecommerce.category'].search([('platform_id','=', self.platform_id.id),('platform_categ_idn','=',categ['parent_id'])])[:1]
                if temp_parent:
                    vals = {
                        'name': categ['category_name'],
                        'platform_id': self.platform_id.id,
                        'platform_categ_idn': categ['category_id'],
                        'platform_parent_categ_idn': categ['parent_id'],
                        'parent_id': temp_parent.id
                        }
                    self.env['ecommerce.category'].create(vals)
                else:
                    vals = {
                        'name': categ['category_name'],
                        'platform_id':self.platform_id.id,
                        'platform_categ_idn': categ['category_id'],
                        'platform_parent_categ_idn': categ['parent_id']
                        }
                    need_prnt.append(self.env['ecommerce.category'].create(vals))

            else:
                vals = {
                    'name': categ['category_name'],
                    'platform_id': self.platform_id.id,
                    'platform_categ_idn': categ['category_id'],
                    'platform_parent_categ_idn': categ['parent_id'],
                    'parent_id': path[-1][0]
                    }
                rec = self.env['ecommerce.category'].create(vals)
                path.append((rec.id, categ['category_id']))

        for categ in need_prnt:
            categ.parent_id = self.env['ecommerce.category'].search([
                ('platform_id','=',self.platform_id.id),
                ('platform_categ_idn','=',categ.platform_parent_categ_idn)])[:1]

    def _vacuum_product_shopee(self):
        self.ensure_one()
        offset, limit = 0,100
        id_list = []
        while True:
            resp = self._py_client_shopee().item.get_item_list(pagination_offset=offset,pagination_entries_per_page=limit)
            id_list += [str(i['item_id']) for i in resp.get('items',[])]
            if not resp.get('more'): break
            offset += limit
        self.env['ecommerce.product.template'].search([('shop_id','=',self.id),('platform_item_idn','not in',id_list)]).unlink()


    def _sync_product_shopee(self, **kw):
        self.ensure_one()
        model = self.env['ecommerce.product.template']
        kw.setdefault('pagination_offset', 0)
        kw.setdefault('pagination_entries_per_page', 100)
        if self._last_product_sync:
            kw.setdefault('update_time_to', int(datetime.now().timestamp()))
            kw.setdefault('update_time_from', int(self._last_product_sync.timestamp()))
        resp = self._py_client_shopee().item.get_item_list(**kw)
        for item in resp['items']:
            if item['status'] == 'DELETED': 
                continue
            details = self._py_client_shopee().item.get_item_detail(item_id=item.get('item_id',0)).get('item',{})
            tmpl = model.search([
                ('shop_id', '=', self.id),
                ('platform_item_idn','=', str(item.get('item_id')))
                ])
            if tmpl:
                for v in details.get("variations", []):
                    p = tmpl.ecomm_product_product_ids.filtered(lambda p: p.platform_variant_idn == str(v.get('variation_id')))
                    if p:
                        p.write({
                            'name': v.get('name'),
                            'sku': v.get('variation_sku'),
                            'price': v.get('price'),
                        })
                    else:
                        tmpl.write({
                            'ecomm_product_product_ids': [(0,_,{
                                'name': v.get('name'),
                                'platform_variant_idn': str(v.get('variation_id')),
                                'sku': v.get('variation_sku'),
                                'price': v.get('price'),
                            })]
                        })
                l_id = len(tmpl.ecomm_product_image_ids)
                l_i = len(details.get("images",[]))
                tmpl.write({
                    'name': details.get('name',False),
                    'description': details.get('description',False),
                    'platform_item_idn': str(item.get('item_id')),
                    'sku': item.get('item_sku'),
                    'price': item.get('price'),
                    'ecomm_product_image_ids': [(1, tmpl.ecomm_product_image_ids[i].id, {
                        'sequence': i,
                        'res_model': 'ecommerce.product.template',
                        'image_url': i < l_i and details['images'][i] or False
                    }) if i < l_id else (0, _, {
                        'sequence': i,
                        'res_model': 'ecommerce.product.template',
                        'image_url': details['images'][i]
                    }) for i in range(max(l_id,l_i))],
                    '_last_sync': datetime.now(),
                })
            else:
                model.create({
                    'name': details.get('name',False),
                    'description': details.get('description',False),
                    'shop_id': self.id,
                    'platform_item_idn': str(item.get('item_id')),
                    'sku': item.get('item_sku'),
                    'price': item.get('price'),
                    '_last_sync': datetime.now(),
                    'ecomm_product_image_ids': [(0, _, {
                        'sequence': i,
                        'res_model': 'ecommerce.product.template',
                        'image_url': url
                    }) for i, url in enumerate(details.get("images",[]))],
                    'ecomm_product_product_ids': [(0, _, {
                        'name': v.get('name'),
                        'platform_variant_idn': str(v.get('variation_id')),
                        'sku': v.get('variation_sku'),
                        'price': v.get('price'),
                    }) for v in details.get("variations", [])],
                })
        if resp.get('more'):
            kw['pagination_offset'] += kw['pagination_entries_per_page']
            self._sync_product_shopee(**kw)
        else:
            self._last_product_sync = datetime.now()


    @api.multi
    def _order_status_push_shopee(self, ordersn, status, update_time):
        for shop in self:
            if status == 'UNPAID': shop._new_order_shopee(ordersn)
            else: shop._update_order_shopee(ordersn, status, update_time)
            return True

    def _new_order_shopee(self, ordersn, detail = False):
        order = self.env['sale.order'].search([('ecommerce_shop_id','=',self.id),('client_order_ref','=',ordersn)])[:1]
        if order: return order
        detail = detail or self._py_client_shopee().order.get_order_detail(ordersn_list=[ordersn])['orders'][0]
        address = detail['recipient_address']
        partner_vals = {
                'phone': address['phone'],
                'name': address['name'],
                'ref': detail['buyer_username'],
                }
        splits = address['full_address'].split(address['district'] or address['city'] or address['state'] or None)
        shipping_address = {
                'country_id': self.env['res.country'].search([('code','=',address['country'])]).id,
                'zip': address['zipcode'],
                'state_id': self.env['res.country.state'].search([('name','=',address['state'])]).id,
                'city': address['city'],
                'street2': address['district'],
                'street': splits and splits[0].rstrip(', ')
                }

        partner_id = self.env['res.partner'].search([
            ('type','!=','delivery'),
            ('phone','=',partner_vals['phone'])
            ])[:1] or self.env['res.partner'].create(partner_vals)

        shipping_ids = partner_id.child_ids.filtered(lambda child: all(child[field].id == val if isinstance(child[field],models.Model) else child[field].casefold() == val.casefold() for field, val in shipping_address.items()))

        if shipping_ids: 
            shipping_id = shipping_ids[0]
        else:
            shipping_address.update({
                'type': 'delivery',
                'parent_id': partner_id.id,
                'phone': address['phone'],
                })
            shipping_id = self.env['res.partner'].create(shipping_address)

        order = self.env['sale.order'].create({
                'ecommerce_shop_id' : self.id,
                'team_id': self.team_id and self.team_id.id,
                'client_order_ref': ordersn,
                'partner_id': partner_id.id,
                'partner_shipping_id': shipping_id.id,
                'order_line':[(0, _, {
                    'product_id' : item['variation_id'] and self.env['ecommerce.product.product'].search([
                        ('platform_variant_idn','=',str(item['variation_id'])),
                        ('ecomm_product_tmpl_id.shop_id','=',self.id)
                    ]).product_product_id.id or self.env['ecommerce.product.template'].search([
                        ('platform_item_idn','=',str(item['item_id']))
                    ]).product_product_id.id or self.env.ref("connector_shopee.shopee_product_product_default").id,
                    'name': '{}{}'.format(item['item_name'], item.get('variation_name',False) and ' ({})'.format(item['variation_name']) or ''),
                    'price_unit': item['variation_discounted_price'] != '0' and item['variation_discounted_price'] or item['variation_original_price'],
                    'product_uom_qty': item['variation_quantity_purchased'],
                    #'route_id': self.route_id.id,
                    }) for item in detail['items']], 
                })
        return order


    def _update_order_shopee(self, ordersn, status, update_time, detail=False):
        order = self.env['sale.order'].search([('ecommerce_shop_id','=',self.id),('client_order_ref','=',ordersn)])[:1] or self._new_order_shopee(ordersn, detail=detail)
        if status in ['READY_TO_SHIP','SHIPPED']:
            if order.state in ['draft','sent']: 
                order.action_confirm()
        elif status == 'CANCELLED':
            if order.state in ['draft', 'sent']:
                order.action_cancel()
        elif status == 'COMPLETED':
            if order.state == 'sale': order.action_done()
        return order

