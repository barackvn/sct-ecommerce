# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests, logging, pyshopee

_logger = logging.getLogger(__name__)

class eCommercerShop(models.Model):
    _inherit = 'ecommerce.shop'

    def _auth_shopee(self):
        self.ensure_one()
#        client_name = self._cr.dbname
        redirect_url = "https://nutishop.scaleup.top/connector_ecommerce/{}/auth".format(self.id)
#        req = requests.post(url=url, data={'client':client_name,'client_shop_id': self.id, 'name': self.name})
        return {
            "type": "ir.actions.act_url",
            "url": self._py_client_shopee().shop.authorize(redirect_url=redirect_url),
            "target": "new",
        }

    def _deauth_shopee(self):
        self.ensure_one()
        redirect_url = "https://nutishop.scaleup.top/connector_ecommerce/{}/deauth".format(self.id)
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

#    def test(self):
#        _logger.info(self.ids)
#        _logger.info(self.id)
#        _logger.info(self[:1].id)
#        _logger.info(self[:1].name)
#        _logger.info(self.name)


    def _py_client_shopee(self):
        self.ensure_one()
        return pyshopee.Client(self.ecomm_shop_idn, self.platform_id.partner_id, self.platform_id.key)

    def _get_categories_shopee(self):
        #should use ref, later
        platform_id = self.env['ecommerce.platform'].search([('platform', '=','shopee')])[:1].id
        
        categs = self._py_client_shopee().item.get_categories().get('categories')
        path = [(False,0)] # categ (id,idn)
        rec = None
        need_prnt = []
        for categ in categs:
            temp = path[:]
            while path and path[-1][1] != categ['parent_id']: 
                path.pop()
            if not path:
                path = temp[:]
                temp_parent = self.env['ecommerce.category'].search([('platform_id','=', platform_id),('platform_categ_idn','=',categ['parent_id'])])[:1]
                if temp_parent:
                    vals = {
                        'name': categ['category_name'],
                        'platform_id': platform_id,
                        'platform_categ_idn': categ['category_id'],
                        'platform_parent_categ_idn': categ['parent_id'],
                        'parent_id': temp_parent.id
                        }
                    self.env['ecommerce.category'].create(vals)
                else:
                    vals = {
                        'name': categ['category_name'],
                        'platform_id': platform_id,
                        'platform_categ_idn': categ['category_id'],
                        'platform_parent_categ_idn': categ['parent_id']
                        }
                    need_prnt.append(self.env['ecommerce.category'].create(vals))

            else:
                vals = {
                    'name': categ['category_name'],
                    'platform_id': platform_id,
                    'platform_categ_idn': categ['category_id'],
                    'platform_parent_categ_idn': categ['parent_id'],
                    'parent_id': path[-1][0]
                    }
                rec = self.env['ecommerce.category'].create(vals)
                path.append((rec.id, categ['category_id']))

        for categ in need_prnt:
            categ.parent_id = self.env['ecommerce.category'].search([
                ('platform_id','=',platform_id),
                ('platform_categ_idn','=',categ.platform_parent_categ_idn)])[:1]

    def _sync_product_unlink_diff_shopee(self):
        self.ensure_one()
        platform_id = self.env['ecommerce.platform'].search([('platform', '=','shopee')])[:1].id
        for tmpl in self.ecomm_product_tmpl_ids:
            resp = self._py_client_shopee().item.get_item_detail(item_id=int(tmpl.platform_item_idn))
            item = resp.get('item')
            if any((
                resp.get('error') == "error_not_exists",
                item and not item['item_sku'] and all((not v["variation_sku"] for v in item["variations"])),
                item and item['item_sku'] not in tmpl.product_tmpl_id.product_variant_ids.mapped('default_code') and all((v["variation_sku"] not in  tmpl.product_tmpl_id.product_variant_ids.mapped('default_code') for v in item["variations"]))
                )):  tmpl.unlink()
            

    def _sync_product_sku_match_shopee(self, offset=0, limit=100):
        self.ensure_one()
        platform_id = self.env['ecommerce.platform'].search([('platform', '=','shopee')])[:1].id
        resp = self._py_client_shopee().item.get_item_list(pagination_offset=offset, pagination_entries_per_page=limit)
        items = resp.get('items')

        for item in items:
            item_idn = str(item.get('item_id',0))
#            _logger.info(item.get('item_sku'))
            if item.get("variations",[]): 
                tmpls = self.env['product.template'].search([
                    ('product_variant_ids.default_code','in',[v.get("variation_sku",False)]) for v in item.get("variations",[])
                    ])
                if tmpls: 
                    details = self._py_client_shopee().item.get_item_detail(item_id=item.get('item_id',0)).get('item',{})
                for tmpl in tmpls:
                    if item_idn not in tmpl.shopee_product_tmpl_ids.mapped('platform_item_idn'):
                        self.env['ecommerce.product.template'].create({
                            'name': details.get('name',False),
                            'description': details.get('description',False),
                            'shop_id': self.id,
                            'platform_item_idn': item_idn,
                            'product_tmpl_id': tmpl.id,
                            'ecomm_product_product_ids': [(0, _, {
                                'name': v.get('name'),
                                'platform_variant_idn': str(v.get('variation_id')),
                                'product_product_id': tmpl.product_variant_ids.filtered(lambda r: r.default_code == v.get("variation_sku"))[:1].id,
                                }) for v in details.get("variations", [])],
                            })
                        if not tmpl.shopee_product_sample_id:
                            details.update({
                                'platform_id': platform_id,
                                'ecomm_categ_id': self.env['ecommerce.category'].search([
                                    ('platform_id','=',platform_id),
                                    ('platform_categ_idn','=',details.get('category_id'))
                                    ]).id,
                                'product_tmpl_id': tmpl.id,
                                })
                            self.env['shopee.product.sample'].create(details)
            elif item.get('item_sku',''): 
                prods = self.env['product.product'].search([('default_code','=',item.get('item_sku','').strip())])
#                _logger.info(prods)
                if prods: 
                    details = self._py_client_shopee().item.get_item_detail(item_id=item.get('item_id',0)).get('item',{})
                for prod in prods:
                    if item_idn not in prod.product_tmpl_id.shopee_product_tmpl_ids.mapped('platform_item_idn'):
                        self.env['ecommerce.product.template'].create({
                            'name': details.get('name',False),
                            'description': details.get('description',False),
                            'shop_id': self.id,
                            'platform_item_idn': item_idn,
                            'product_tmpl_id': prod.product_tmpl_id.id,
                            'product_product_id': prod.id,
                            })
                        if not prod.product_tmpl_id.shopee_product_sample_id:
                            details.update({
                                'platform_id': platform_id,
                                'ecomm_categ_id': self.env['ecommerce.category'].search([
                                    ('platform_id','=',platform_id),
                                    ('platform_categ_idn','=',details.get('category_id'))
                                    ]).id,
                                'product_tmpl_id': prod.product_tmpl_id.id,
                                })
                            self.env['shopee.product.sample'].create(details)
                
        if resp['more']:
            self._sync_product_sku_match_shopee(offset=offset+limit, limit=limit)


    @api.multi
    def _order_status_push_shopee(self, ordersn, status, update_time):
        for shop in self:
            if status == 'UNPAID': shop._new_order_shopee(ordersn, status, update_time)
            else: shop._update_order_shopee(ordersn, status, update_time)
            return True

    def _new_order_shopee(self, ordersn, status, update_time, resp = False):
        resp = resp or self._py_client_shopee().order.get_order_detail(ordersn_list=[ordersn])
        shopee_orders = resp.get('orders')
        shopee_order = shopee_orders[0]
        address = shopee_order['recipient_address']
        partner_vals = {
                'phone': address['phone'],
                'name': address['name'],
                'ref': shopee_order['buyer_username'],
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

        order = self.env['sale.order'].create({
                'ecommerce_shop_id' : self.id,
                'team_id': self.team_id and self.team_id.id,
                'client_order_ref': ordersn,
                'partner_id': shipping_id.id,
                'order_line':[(0, _, {
                    'product_id' : item['variation_id'] and self.env['ecommerce.product.product'].search([
                        ('platform_variant_idn','=',str(item['variation_id']))
                    ]).product_product_id.id or self.env['ecommerce.product.template'].search([
                        ('platform_item_idn','=',str(item['item_id']))
                    ]).product_product_id.id or self.env.ref("connector_shopee.shopee_product_product_default").id,
                    'name': '{}{}'.format(item['item_name'], item.get('variation_name',False) and ' ({})'.format(item['variation_name']) or ''),
                    'price_unit': item['variation_discounted_price'] != '0' and item['variation_discounted_price'] or item['variation_original_price'],
                    'product_uom_qty': item['variation_quantity_purchased'],
                    #'route_id': self.route_id.id,
                    }) for item in shopee_order['items']], 
                })
        return order


    def _update_order_shopee(self, ordersn, status, update_time):
        order = self.env['sale.order'].search([('ecommerce_shop_id','=',self.id),('client_order_ref','=',ordersn)])[:1] or self._new_order_shopee(ordersn, status, update_time)
        if status in ['READY_TO_SHIP','SHIPPED']:
            if order.state == 'draft': order.action_confirm()
        elif status == 'CANCELLED':
            order.action_cancel()
        elif status == 'COMPLETED':
            if order.state == 'sale': order.action_done()
        return order

        #elif status == 'TO_RETURN':
        #    shopee_pick_ids = order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'] and r.picking_type_id.code == 'outgoing' and r.location_id.id == self.location_id.id)
        #    for pick_id in shopee_pick_ids: pick_id.action_cancel()
        #    my_pick_ids = order.picking_ids.filtered(lambda r: r.state == 'done' and r.picking_type_id.code == 'internal' and r.location_dest_id.id == self.location_id.id)
        #    for pick_id in my_pick_ids: 
        #        wiz = self.env['stock.picking.return'].create({'picking_id': pick_id.id}).create_returns()
        #elif status == 'COMPLETED':
        #    if order.state == 'sale': order.action_done()
        #    pick_ids = order.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'] and r.picking_type_id.code == 'outgoing' and r.location_id.id == self.location_id.id)
        #    for pick_id in pick_ids:
        #        wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, pick_id.id)]}).process()



#class shopee_state_map(models.Model):
#    _name = 'shopee_api_client.shopee_state_map'
#
#    shopee_state = fields.Selection([
#        ('UNPAID','UNPAID'),
#        ('READY_TO_SHIP','READY_TO_SHIP'),
#        ('RETRY_SHIP','RETRY_SHIP'),
#        ('IN_CANCEL','IN_CANCEL'),
#        ('SHIPPED','SHIPPED'),
#        (''])

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
