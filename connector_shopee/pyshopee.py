from pyshopee import client
from odoo import exceptions

class Client(client.Client):
    def _build_response(self, resp):
        body = super(Client, self)._build_response(resp)
        if "error" not in body:
            return body
        else:
            raise exceptions.UserError(f'Shopee Error Info: {body["msg"]}')

