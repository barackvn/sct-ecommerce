# -*- coding: utf-8 -*-
#create for structure purpose, not in use, might be use in future updates
from odoo import fields, models, api, _

class eCommercePlatform(models.Model):
    _name = 'ecommerce.platform'

    name = fields.Char()
    platform = fields.Selection([])
    partner_id = fields.Integer()
    key = fields.Char()

    @api.model
    def cron_sync_categories(self):
        for platform in self.env['ecommerce.platform'].search([]):
            self.env['ecommerce.shop'].search([('platform_id','=',platform.id),('state','=','auth')])[:1].get_categories()
