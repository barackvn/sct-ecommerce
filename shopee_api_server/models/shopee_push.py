# -*- coding: utf-8 -*-

from odoo import fields, api, models, _

class ShopeeServerHook(models.Model):
    _name = 'shopee_server.hook'

    shop_id = fields.Integer()
    code = fields.Integer()
    success = fields.Integer()
    extra = fields.Text()
    timestamp = fields.Integer()
    data = fields.Text()
    executed = fields.Boolean()



