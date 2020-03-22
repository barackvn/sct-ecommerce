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
            ('id_platform_uniq', 'unique (ecommerce_paltform_id, logistic_idn)', 'This logistic already exists !')
            ]

