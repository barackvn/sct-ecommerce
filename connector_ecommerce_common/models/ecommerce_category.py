# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

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
