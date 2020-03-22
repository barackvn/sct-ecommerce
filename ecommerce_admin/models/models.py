# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class ecommerce_admin(models.Model):
#     _name = 'ecommerce_admin.ecommerce_admin'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100