# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging
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
        for _ in self:
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

class eCommerceProductTemplateAttributeLine(models.Model):
    _name = 'ecommerce.product.template.attribute.line'
    _order = 'sequence, attr_id, id'

    attr_id = fields.Many2one('product.attribute', string='Attribute', index=True)
    name = fields.Char(required=True)
    ecomm_product_tmpl_id = fields.Many2one('ecommerce.product.template', ondelete='cascade', required=True, index=True)
    sequence = fields.Integer()
    line_value_ids = fields.One2many('ecommerce.product.template.attribute.line.value', 'attr_line_id', string="Attribute Values", copy=True)

    @api.onchange('attr_id')
    def onchange_attr_id(self):
        if self.attr_id:
            self.name = self.attr_id.name

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.name = self.name.strip()

class eCommerceProductTemplateAttributeLineValue(models.Model):
    _name = 'ecommerce.product.template.attribute.line.value'
    _order = 'attr_line_id, sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer()
    attr_line_id = fields.Many2one('ecommerce.product.template.attribute.line', index=True)
    attr_id = fields.Many2one('product.attribute', related='attr_line_id.attr_id', readonly=True)
    value_id = fields.Many2one('product.attribute.value', domain="[('attribute_id', '=', attr_id)]")
    ecomm_product_image_ids = fields.One2many('ecommerce.product.image', 'res_id', 'Images', auto_join=True, domain = lambda self: [('res_model','=',self._name)], copy=True)

    @api.onchange('value_id')
    def onchange_value_id(self):
        if self.value_id:
            self.name = self.value_id.name

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.name = self.name.strip()
        if self.attr_line_id.ecomm_product_tmpl_id.platform_id:
            getattr(
                self,
                f'_onchange_name_{self.attr_line_id.ecomm_product_tmpl_id.platform_id.platform}',
            )()

    def unlink(self):
        self.mapped('ecomm_product_image_ids').unlink()
        return super(eCommerceProductTemplateAttributeLineValue, self).unlink()

        
