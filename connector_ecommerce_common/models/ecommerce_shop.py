# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class eCommerceShop(models.Model):
    _name = 'ecommerce.shop'

    name = fields.Char()
    ecomm_shop_name = fields.Char()
    ecomm_shop_idn = fields.Integer()
    state=fields.Selection([('auth','Authorized'),('no','Not Authorized'),('deauth','Deauthorized')],default='no')
    team_id = fields.Many2one('crm.team', 'Sales Team')
    platform_id = fields.Many2one('ecommerce.platform', required = True)
    is_main = fields.Boolean(string=_("Main Shop on Platform"))
    ecomm_product_tmpl_ids = fields.One2many('ecommerce.product.template','shop_id')
    ecomm_product_tmpl_count = fields.Integer(compute='_compute_tmpl_count')
    auto_update_stock = fields.Boolean()
    _last_sku_sync = fields.Datetime(readonly=True)
    _last_order_sync = fields.Datetime(readonly=True)
    _last_product_sync = fields.Datetime(readonly=True)

    @api.depend('ecomm_product_tmpl_ids')
    def _compute_tmpl_count(self):
        for shop in self:
            shop.ecomm_product_tmpl_count = len(shop.ecomm_product_tmpl_ids)

    @api.multi
    def do_action(self, action):
        for shop in self:
            getattr(shop, "_{}_{}".format(action, shop.platform_id.platform))
    
    def auth(self):
        self.ensure_one()
        return getattr(self, "_auth_{}".format(self.platform_id.platform))()

    def deauth(self):
        self.ensure_one()
        return getattr(self, "_deauth_{}".format(self.platform_id.platform))()

    def sync_product_sku_match(self, **kw):
        self.ensure_one()
        return getattr(self, "_sync_product_sku_match_{}".format(self.platform_id.platform))(**kw)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    ecommerce_shop_id = fields.Many2one('ecommerce.shop', string=_("eCommerce Shop"))
