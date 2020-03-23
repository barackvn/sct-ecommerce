#-*- coding: utf-8 -*-

from odoo import api, fields, models, _
import requests, logging, lazop

class eCommerceShop(models.Model):
    _inherit = 'ecommerce.shop'

    #region = fields.Selection([])
    url = fields.Char('URL endpoint', help="Region url endpoint used for lazop")
    access_token = fields.Char()
    refresh_token = fields.Char()
    refresh_expires_in = fields.Float()
    account = fields.Char()


    def _py_client_lazada_request(self, *args, **kwargs):
        self.ensure_one()
        client = lazop.LazopClient(self.url, self.platform_id.partner_id, self.platform_id.key)
        request = lazop.LazopRequest(*args)
        for k,v in kwargs.items():
            request.add_api_param(k,v)
        response = client.execute(request, access_token)
        return response.body
    
    def _get_info_lazada(self):
        pass

    def _auth_lazada(self):
        params = {
            'client_id': self.platform_id.partner_id,
            'redirect_uri': 'https://nutishop.scaleup.top/connector_ecommerce/{}/auth'.format(self.platform_id.id),
            'response_type': 'code',
            'force_auth': True
            }
        return {
            'type': 'ir.actions.act_url',
            'url' : requests.Request('GET', 'https://auth.lazada.com/oauth/authorize', params=params).prepare().url,
            'target': 'new'
            }



