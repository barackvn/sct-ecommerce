# -*- coding: utf-8 -*-

from odoo import models, api, fields, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        if super(SaleOrder, self).action_confirm():
            for record in self:
                invoice_ids = record.action_invoice_create(final=True)
            return True

    @api.multi
    def action_cancel(self):
        if super(SaleOrder, self).action_cancel():
            for inv in self.invoice_ids.filtered(lambda r: r.state == 'draft'):
                inv.action_cancel()
            return True

