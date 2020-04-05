# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api, _

class eCommerceCategory(models.Model):
    _name = 'ecommerce.category'

    name = fields.Char(required=True, translate=True)
    platform_id = fields.Many2one('ecommerce.platform')
    platform_categ_idn = fields.Integer()
    platform_parent_categ_idn = fields.Integer()
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

class eCommerceCategorySelector(models.Model):
    _name = 'ecommerce.category.selector'
    _rec_name = 'category_name'

    platform_id = fields.Many2one('ecommerce.platform')
    tier1 = fields.Many2one('ecommerce.category', domain="[('platform_id', '=', platform_id),('parent_id','=',False)]")
    tier2 = fields.Many2one('ecommerce.category', domain="[('parent_id', '=', tier1)]")
    tier3 = fields.Many2one('ecommerce.category', domain="[('parent_id', '=', tier2)]")
    tier4 = fields.Many2one('ecommerce.category', domain="[('parent_id', '=', tier3)]")
    ecomm_categ_id = fields.Many2one('ecommerce.category')
    category_name = fields.Char(string=_("Category"), related='ecomm_categ_id.complete_name', readonly=True)

    @api.onchange('tier1','tier2','tier3','tier4')
    def onchange_tiers(self):
        self.ecomm_categ_id = self.tier4 or self.tier3 or self.tier2 or self.tier1

    @api.onchange('tier1')
    def onchange_tier1(self):
        self.tier2 = False

    @api.onchange('tier2')
    def onchange_tier2(self):
        self.tier3 = False

    @api.onchange('tier3')
    def onchange_tier3(self):
        self.tier4 = False
    
    def action_create_sample(self):
        self.ensure_one()
        return getattr(self, "_action_create_sample_{}".format(self.platform_id.platform))()
                                                        
