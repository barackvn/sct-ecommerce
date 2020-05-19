# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_move_vals(self, journal=None):
        move_vals = super(AccountPayment, self)._get_move_vals(journal=journal)
        if not move_vals.get('ref'):
            move_vals['ref'] = self.name
        return move_vals
