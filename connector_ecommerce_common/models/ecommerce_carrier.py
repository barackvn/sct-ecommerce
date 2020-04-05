#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class eCommerceCarrier(models.Model):
    _name = 'ecommerce.carrier'

    logistic_idn = fields.Integer("Logistic eCommerce ID")
    name = fields.Char()
    enable = fields.Boolean()
    default = fields.Boolean()
    cod = fields.Boolean()
    carrier_id = fields.Many2one('delivery.carrier')
    platform_id = fields.Many2one('ecommerce.platform')

    _sql_constraint = [
            ('id_platform_name_id_uniq', 'unique (platform_id, logistic_idn, name)', 'This logistic already exists !')
            ]

class eCommerceShopCarrier(models.Model):
    _name = 'ecommerce.shop.carrier'
    _rec_name = 'ecomm_carrier_id'

    ecomm_carrier_id = fields.Many2one('ecommerce.carrier')
    shop_id = fields.Many2one('ecommerce.shop')
    enable = fields.Boolean()
    default = fields.Boolean()
    cod = fields.Boolean()

class eCommerceProductCarrier(models.Model):
    _name = 'ecommerce.product.carrier'
    _rec_name = 'ecomm_carrier_id'

    ecomm_carrier_id = fields.Many2one('ecommerce.carrier')
    ecomm_product_tmpl_id = fields.Many2one('ecommerce.product.template')
    enable = fields.Boolean()
