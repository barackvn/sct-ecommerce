# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api, _

class eCommerceCategory(models.Model):
    _name = 'ecommerce.category'
    _description = "eCommerce Product Category"
    _rec_name = 'complete_name'
    _order = 'complete_name'

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

    @api.model
    def name_get(self):
        if self._context.get('short_name'): 
            return [(record.id, "{}".format(record.name)) for record in self]
        else:
            return super(eCommerceCategory, self).name_get()

class eCommerceCategorySelector(models.Model):
    _name = 'ecommerce.category.selector'
    _rec_name = 'ecomm_categ_id'

    platform_id = fields.Many2one('ecommerce.platform')
    tier1 = fields.Many2one('ecommerce.category', domain="[('platform_id', '=', platform_id),('parent_id','=',False)]", context="{'short_name':True}")
    tier2 = fields.Many2one('ecommerce.category', domain="[('parent_id', '=', tier1)]", context="{'short_name':True}")
    tier3 = fields.Many2one('ecommerce.category', domain="[('parent_id', '=', tier2)]", context="{'short_name':True}")
    tier4 = fields.Many2one('ecommerce.category', domain="[('parent_id', '=', tier3)]", context="{'short_name':True}")
    end_node = fields.Boolean(compute='compute_end_node')
    ecomm_categ_id = fields.Many2one('ecommerce.category', context="{'short_name':False}")
    category_name = fields.Char(string=_("Category"), related='ecomm_categ_id.complete_name', readonly=True)

    @api.depends('ecomm_categ_id')
    def compute_end_node(self):
        for s in self:
            s.end_node = s.ecomm_categ_id and not s.ecomm_categ_id.child_ids

    @api.onchange('ecomm_categ_id')
    def onchange_categ(self):
        tier = self.tier4 or self.tier3 or self.tier2 or self.tier1
        if self.ecomm_categ_id.id == tier.id:
            return
        c = self.ecomm_categ_id
        tree = [c]
        while c.parent_id:
            c = c.parent_id
            tree.insert(0,c)
        self.with_context(short_name=False).update({'tier{}'.format(i+1): c.id for i,c in enumerate(tree)})

    @api.onchange('tier1','tier2','tier3','tier4')
    def onchange_tiers(self):
        tier = self.tier4 or self.tier3 or self.tier2 or self.tier1
        self.with_context(short_name=False).update({'ecomm_categ_id': tier.id})

    @api.onchange('tier1')
    def onchange_tier1(self):
        self.tier2 = False

    @api.onchange('tier2')
    def onchange_tier2(self):
        self.tier3 = False

    @api.onchange('tier3')
    def onchange_tier3(self):
        self.tier4 = False
    
    def action_create_preset(self):
        self.ensure_one()
        ctx = {
            'default_ecomm_categ_selector_id': self.id,
            'default_platform_id': self.env.context.get('default_platform_id'),
            'platform': self.env.context.get('platform'),
            'default_product_tmpl_id': self.env.context.get('default_product_tmpl_id')
        }
        return getattr(self, "_action_create_preset_{}".format(self.platform_id and self.platform_id.platform or self.env.context.get('platform')))(ctx)
                                                        
