# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class eCommerceShop(models.Model):
    _name = 'ecommerce.shop'

    name = fields.Char()
    ecomm_shop_name = fields.Char()
    ecomm_shop_idn = fields.Integer()
    state=fields.Selection([('auth','Authorized'),('no','Not Authorized'),('de-auth','Deauthorized')],default='no')
    team_id = fields.Many2one('crm.team', 'Sales Team')
    platf_id = fields.Many2one('ecommerce.platform', required = True)
    is_main = fields.Boolean(string=_("Main Shop on Platform"))
    ecomm_product_tmpl_ids = fields.One2many('ecommerce.product.template','shop_id')

    @api.multi
    def do_action(self, action):
        for shop in self:
            getattr(shop, "_{}_{}".format(action, shop.platform_id.platform))


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    ecommerce_shop_id = fields.Many2one('ecommerce.shop', string=_("eCommerce Shop"))
