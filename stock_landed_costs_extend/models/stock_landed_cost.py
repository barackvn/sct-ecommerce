#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def _default_account_journal_id(self):
        """Take the journal configured in the company, else fallback on the stock journal."""
        lc_journal = self.env['account.journal']
        if ir_property := self.env['ir.property'].search(
            [
                ('name', '=', 'property_stock_journal'),
                ('company_id', '=', self.env.user.company_id.id),
            ],
            limit=1,
        ):
            lc_journal = ir_property.get_by_record()
        return lc_journal

    account_journal_id = fields.Many2one(
        'account.journal', 'Account Journal',
        required=True, states={'done': [('readonly', True)]}, default=lambda self: self._default_account_journal_id())


