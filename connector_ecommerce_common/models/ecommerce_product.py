# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class eCommerceCategory(models.Model):
    _name = 'ecommerce.category'

    name = fields.Char(required=True, translate=True)
    platf_id = fields.Many2one('ecommerce.platform')
    platf_categ_idn = fields.Integer()
    platf_parent_categ_idn = fields.Integer()
    parent_id = fields.Many2one('ecommerce.category', 'Parent Category')
    child_ids = fields.One2many('ecommerce.category', 'parent_id')
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)


    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '{} > {}'.format(category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
        return True

class eCommerceAttribute(models.Model):
    _name = 'ecommerce.attribute'
    
    name = fields.Char('Attribute', required=True, translate=True)
    platf_id = fields.Many2one('ecommerce.platform', required=True)
    platf_attr_idn = fields.Integer()
    platf_attr__name = fields.Char(help="Some platform identify their attributes by name")
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
    platf_id = fields.Many2one('ecommerce.platform', related='attr_id.platf_id', readonly=True)
    value_ids = fields.Many2many('ecommerce.attribute.value', 'ecommerce_attr_value_sample_attr_line_rel',string='eCommerce Attribute Values')

class eCommerceProductSample(models.AbstractModel):
    _name = 'ecommerce.product.sample'

    name = fields.Char()
    ecomm_categ_id = fields.Many2one('ecommerce.category', required=True)
    platf_id = fields.Many2one('ecommerce.platform', required=True)
    product_tmpl_ids = fields.One2many('product.template', 'ecomm_product_sample_id', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', ondelete='cascade', compute='_compute_product_tmpl_id', inverse='_inverse_product_tmpl_id', store=True)
    category_id = fields.Integer(related='ecomm_categ_id.platf_categ_idn', store=True, readonly=True)
    category_name = fields.Char(string=_("Shopee Category"), related='ecomm_categ_id.complete_name', readonly=True)
    
    @api.depends('product_tmpl_ids')
    def _compute_product_tmpl_id(self):
        for s in self:
            s.product_tmpl_id = s.product_tmpl_ids and s.product_tmpl_ids[0]

    def _inverse_product_tmpl_id(self):
        for s in self:
            s.product_tmpl_ids = (s.product_tmpl_id)

    _sql_constraints = [
            ('platform_product_unique', 'unique(platf_id, product_tmpl_id)','This product sample already exists in this platform')
            ]

class eCommerceProductTemplate(models.Model):
    _name = 'ecommerce.product.template'
    _description = "Product Item (Template) which might contains variants"

    name = fields.Char()
    description = fields.Text()
    shop_id = fields.Many2one('ecommerce.shop', required=True)
    platf_id = fields.Many2one('ecommerce.platform', related="shop_id.platf_id", store=True)
    platf_item_idn = fields.Char(string=_("ID Number"),index=True, required=True)
    ecomm_product_sample_id = fields.Many2one('ecommerce.product.sample')
    product_tmpl_id = fields.Many2one('product.template',required=True, ondelete='cascade')
    product_product_id = fields.Many2one('product.product', string=_("Single Variant"))
    ecomm_product_product_ids = fields.One2many('ecommerce.product.product', 'ecomm_product_tmpl_id', string=_("Variants"))

    def update_stock(self):
        for tmpl in self:
            getattr(tmpl, "_update_stock_{}".format(tmpl.platf_id.platform))()


class eCommerceProductProduct(models.Model):
    _name = 'ecommerce.product.product'
    _description = "Real Product, which might be called as a Variant in some platform"

    name = fields.Char()
    platf_variant_idn = fields.Char(index=True, required=True)
    product_product_id = fields.Many2one('product.product')
    ecomm_product_tmpl_id = fields.Many2one('ecommerce.product.template', ondelete='cascade')
