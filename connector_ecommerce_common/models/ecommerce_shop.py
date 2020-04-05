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
    auto_sync = fields.Boolean()
    carrier_ids = fields.One2many('ecommerce.shop.carrier', 'shop_id', auto_join=True, string=_('Delivery Methods'))
    _last_sku_sync = fields.Datetime(readonly=True)
    _last_order_sync = fields.Datetime(readonly=True)
    _last_product_sync = fields.Datetime(readonly=True)

    @api.depends('ecomm_product_tmpl_ids')
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

    def sync_product(self, **kw):
        for shop in self:
            getattr(shop, "_sync_product_{}".format(shop.platform_id.platform))(**kw)
    
    def match_sku(self):
        for shop in self:
            shop.ecomm_product_tmpl_ids.match_sku()  

    @api.model
    def cron_sync_product(self):
        self.env['ecommerce.shop'].search([('auto_sync','=',True)]).sync_product()

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    ecommerce_shop_id = fields.Many2one('ecommerce.shop', string=_("eCommerce Shop"))
