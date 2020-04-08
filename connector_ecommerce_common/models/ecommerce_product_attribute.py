# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class eCommerceAttribute(models.Model):
    _name = 'ecommerce.attribute'

    name = fields.Char('Attribute', required=True, translate=True)
    platform_id = fields.Many2one('ecommerce.platform', required=True)
    platform_attr_idn = fields.Integer()
    platform_attr__name = fields.Char(help="Some platform identify their attributes by name")
    value_ids = fields.One2many('ecommerce.attribute.value', 'attr_id', string =_('Values'))
    attr_type = fields.Char()
    input_type = fields.Char()
    allow_input = fields.Boolean(compute='_compute_allow_input', store=True)
    mandatory = fields.Boolean()

    @api.depends('input_type')
    def _compute_allow_input(self):
        for attr in self:
            return True
            #getattr(attr, '_compute_allow_input_{}'.format(attr.platform_id.platform))()

class eCommerceAttributeValue(models.Model):
    _name = 'ecommerce.attribute.value'

    name = fields.Char(string='Value', required=True, translate=True)
    attr_id = fields.Many2one('ecommerce.attribute', string='eCommerce Attribute', ondelete='cascade', required=True)

    _sql_constraints = [
            ('value_company_uniq', 'unique (name, attr_id)', 'This attribute value already exists !')
            ]

class eCommerceProductPresetAttributeLine(models.Model):
    _name = 'ecommerce.product.preset.attribute.line'
    _rec_name = 'attr_id'

    attr_id = fields.Many2one('ecommerce.attribute', string='eCommerce Attribute', ondelete='restrict', required=True)
    platform_id = fields.Many2one('ecommerce.platform', related='attr_id.platform_id', readonly=True)
    mandatory = fields.Boolean(related='attr_id.mandatory', readonly=True)
    value_id = fields.Many2one('ecommerce.attribute.value')
    res_id = fields.Integer()
    res_model = fields.Char(store=True)



