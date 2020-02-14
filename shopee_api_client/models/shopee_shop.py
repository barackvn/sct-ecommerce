# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests, logging, pyshopee

_logger = logging.getLogger(__name__)

class ShopeeClientShop(models.Model):
    _name = 'shopee_client.shop'

    name = fields.Char()
    shopee_name = fields.Char()
    shop_id = fields.Integer()
    state=fields.Selection([('auth','Authorized'),('no','Not Authorized'),('de-auth','Deauthorized')],default='no')
    team_id = fields.Many2one('crm.team', 'Sales Team')
    partner_id = fields.Integer()
    key = fields.Char()
    #route_id = fields.Many2one('stock.location.route', 'Route')
    #location_id =fields.Many2one('stock.location', 'Location')

    @api.multi
    def auth(self):
        self.ensure_one()
        client_name = self._cr.dbname
        url = "https://shopee.scaleup.top/shopee_server/shop/request"
        for shop in self:
            req = requests.post(url=url, data={'client':client_name,'client_shop_id': shop.id, 'name': shop.name})
            return {
                "type": "ir.actions.act_url",
                "url": req.text,
                "target": "new",
            }

    def test(self):
        _logger.info(self.ids)
        _logger.info(self.id)
        _logger.info(self[:1].id)
        _logger.info(self[:1].name)
        _logger.info(self.name)

    def pyClient(self):
        return pyshopee.Client(self.shop_id, self.partner_id, self.key)

    @api.multi
    def order_status_push(self, ordersn, status, update_time):
        for shop in self:
            if status == 'UNPAID': shop.new_order(ordersn, status, update_time)
            else: shop.update_order(ordersn, status, update_time)
            return True

    def new_order(self, ordersn, status, update_time):
        resp = self.pyClient().order.get_order_detail(ordersn_list=[ordersn])
        shopee_orders = resp.get('orders')
        shopee_order = shopee_orders[0]
        partner_vals = {
                'phone': shopee_order['recipient_address']['phone'],
                'name': shopee_order['recipient_address']['name'],
                'ref': shopee_order['buyer_username'],
                }
#        partner_id = self.env['res.partner'].search([('phone','=',partner_vals['phone'])])[:1] or self.env['res.partner'].create(partner_vals)

        order = self.env['sale.order'].create({
                'team_id': self.team_id and self.team_id.id,
                'client_order_ref': ordersn,
                'partner_id': self.env['res.partner'].search([('phone','=',partner_vals['phone'])])[:1].id or self.env['res.partner'].create(partner_vals).id,
                'order_line':[(0, _, {
                    'product_id' : self.env['product.product'].search([('default_code','=',item['variation_sku'] or item['item_sku'])])[:1].id or self.env['product.product'].create({
                        'name': item['variation_name'] or item['item_name'],
                        'default_code': item['variation_sku'] or item['item_sku'],
                        'lst_price': item['variation_original_price'],
                        'type': 'product',
                        }).id,
                    'price_unit': item['variation_discounted_price'] != '0' and item['variation_discounted_price'] or item['variation_original_price'],
                    'product_uom_qty': item['variation_quantity_purchased'],
                    #'route_id': self.route_id.id,
                    }) for item in shopee_order['items']], 
                })
        order.message_post(body='Shipping Address: {}'.format(shopee_order['recipient_address']['full_address']))
        return order


    def update_order(self, ordersn, status, update_time):
        order = self.env['sale.order'].search([('team_id','=?',self.team_id.id),('client_order_ref','=',ordersn)])[:1] or self.new_order(ordersn, status, update_time)
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
