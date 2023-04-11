# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.queue_job.job import job
import requests, pyshopee, secrets, urllib, logging

_logger = logging.getLogger(__name__)

PARAMS = {
    "partner_id": "shopee_server.shopee_partner_id",
    "key": "shopee_server.shopee_partner_key",
}

ORDER_MAP = {}


class ShopeeServerClient(models.Model):
    _name="shopee_server.client"

    name = fields.Char("Database Name")
#    db_name = fields.Char("Database name", index=True)

class ShopeeServerShop(models.Model):
    _name="shopee_server.shop"

    name=fields.Char("Name")
    shopee_name=fields.Char()
    client_id = fields.Many2one(comodel_name="shopee_server.client",string= "Client")
    shop_id=fields.Integer("Shopee ID")
    client_shop_id = fields.Integer()
    state=fields.Selection([('auth','Authorized'),('no','Not Authorized'),('de-auth','Deauthorized')], default='no')
    authorize_url = fields.Char('Authorize URL', store=True)
    deauthorize_url = fields.Char('Deauthorize URL', store=True)
    pyClient = pyshopee.Client(0,0,0)
    
    @api.multi
    def _url_get(self):
        partner_id = self.env['ir.config_parameter'].get_param(PARAMS['partner_id'], 0)
        key = self.env['ir.config_parameter'].get_param(PARAMS['key'], '')
        for shop in self:
            redirect_url = (
                f'https://shopee.scaleup.top/shopee_server/shop/{shop.id}/retrieve'
            )
            shop.pyClient = pyshopee.Client(shop.shop_id, partner_id, key)
            shop.authorize_url = shop.pyClient.shop.authorize(redirect_url)
            shop.deauthorize_url = shop.pyClient.shop.cancel_authorize(redirect_url)

    @api.model
    def create(self, vals):
        new_rec = super(ShopeeServerShop, self).create(vals)
        new_rec._url_get()
        return new_rec
    
    def handle_reg_request(self, data):
        if data.get('client'): 
            clients = self.env['shopee_server.client'].search([('name','=',data.get('client'))])
            client = clients and clients[0] or self.env['shopee_server.client'].create({'name':data.get('client')})
            return self.create({'client_id':client.id,'client_shop_id': data.get('client_shop_id'),'name': data.get('name')})
        else:
            return False

    @job
    @api.multi
    def handle_push(self, data):
        for shop in self:
            if data.get('code',0) == 2:
                continue
            if data.get('code',0) == 1:
                url = f"https://{shop.client_id.name}/shopee_client/shop/{shop.client_shop_id}/auth"
                partner_id = self.env['ir.config_parameter'].get_param(PARAMS['partner_id'], 0)
                key = self.env['ir.config_parameter'].get_param(PARAMS['key'], '')
                values = {'shop_id': data.get('shop_id'),'state':'auth', 'partner_id': partner_id, 'key': key}
                shop.pyClient = pyshopee.Client(shop.shop_id, partner_id, key)
                req = requests.post(url=url,data=values)

            elif data.get('code',0) == 3:
                url = f"https://{shop.client_id.name}/shopee_client/shop/{shop.client_shop_id}/order_status"
                req = requests.post(url=url,data=data.get('data'))

            elif data.get('code',0) == 4:
                url = f"https://{shop.client_id.name}/shopee_client/shop/{shop.client_shop_id}/order_tracking_no"
                req = requests.post(url=url,data=data.get('data'))

#    @api.depends()
#    @api.one
#    def shop_authorize(self):
#        client = pyshopee.Client(self.shopee_id, partner_id, key)
#        shop.authorize_url = client.shop.authorize(PARAMS['redirect_url'])
#        return {
#            'type': 'ir.actions.act_url',
#            'url': shop.authorize_url,
#            'target': 'new',
#        }


