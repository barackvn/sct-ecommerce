#-*- coding: utf-8 -*-

from odoo import fields, models, api, _

class eCommerceCategorySelector(models.TransientModel):
    _name = 'ecommerce.category.selector'

    platform_id = fields.Many2one('ecommerce.platform')
    tier1 = fields.Many2one('ecommerce.category', domain="[('platform_id', '=', platform_id),('parent_id','=',False)]")
    tier2 = fields.Many2one('ecommerce.category', domain="[('parent_id', '=', tier1)]")
    tier3 = fields.Many2one('ecommerce.category', domain="[('parent_id', '=', tier2)]")
    tier4 = fields.Many2one('ecommerce.category', domain="[('parent_id', '=', tier3)]")
    ecomm_categ_id = fields.Many2one('ecommerce.category')
    category_name = fields.Char(string=_("Selected Category"), related='ecomm_categ_id.complete_name', readonly=True)

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


    def action_create_preset(self):
        self.ensure_one()
        return getattr(self, "_action_create_preset_{}".format(self.platform_id.platform))() 
