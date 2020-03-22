# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class eCommerceAttribute(models.Model):
    _name = 'ecommerce.attribute'

    name = fields.Char('Attribute', required=True, translate=True)
    platform_id = fields.Many2one('ecommerce.platform', required=True)
    platform_attr_idn = fields.Integer()
    platform_attr__name = fields.Char(help="Some platform identify their attributes by name")
    value_ids = fields.One2many('ecommerce.attribute.value', 'attr_id', 'Values')

class eCommerceAttributeValue(models.Model):
    _name = 'ecommerce.attribute.value'

    name = fields.Char(string='Value', required=True, translate=True)
    attr_id = fields.Many2one('ecommerce.attribute', string='eCommerce Attribute', ondelete='cascade', required=True)

    _sql_constraints = [
            ('value_company_uniq', 'unique (name, attr_id)', 'This attribute value already exists !')
            ]

class eCommerceProductSampleAttributeLine(models.Model):
    _name = 'ecommerce.product.sample.attribute.line'
    _rec_name = 'attr_id'

#    product_sample_id = fields.Many2one('ecommerce.product.sample', string='Product Sample', ondelete='cascade', required=True)
    attr_id = fields.Many2one('ecommerce.attribute', string='eCommerce Attribute', ondelete='restrict', required=True)
    platform_id = fields.Many2one('ecommerce.platform', related='attr_id.platform_id', readonly=True)
    value_ids = fields.Many2many('ecommerce.attribute.value', 'ecommerce_attr_value_sample_attr_line_rel',string='eCommerce Attribute Values')

