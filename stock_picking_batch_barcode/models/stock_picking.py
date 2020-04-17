# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.tools.float_utils import float_compare
import base64, pytz

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    all_quantities_done = fields.Boolean(compute='_compute_all_quantities_done', inverse='_inverse_all_quantities_done', store=True)
    carrier_tracking_ref_barcode = fields.Binary(compute='_compute_carrier_tracking_ref_barcode', store=True)

    @api.depends('move_lines.quantity_done','move_lines.product_uom_qty')
    def _compute_all_quantities_done(self):
        for pick in self:
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if pick.move_lines.filtered(lambda m: m.state not in ('cancel')) and  all(float_compare(move.quantity_done,move.product_uom_qty,precision_digits=precision_digits) == 0 for move in pick.move_lines.filtered(lambda m: m.state not in ('done', 'cancel'))):
                pick.message_post(body='Logistic time stamp: {}'.format(fields.Datetime.now().astimezone(pytz.timezone(self.env.user.tz or 'UTC'))))
                pick.all_quantities_done = True

    def _inverse_all_quantities_done(self):
        for pick in self:
            if pick.all_quantities_done: 
                for l in pick.move_line_ids.filtered(lambda l: l.state not in ('done','cancel')):
                    l.qty_done = l.product_uom_qty
                pick.message_post(body='Logistic time stamp: {}'.format(fields.Datetime.now().astimezone(pytz.timezone(self.env.user.tz or 'UTC'))))
            else: pick.move_line_ids.filtered(lambda l: l.state not in ('done','cancel')).write({'qty_done': 0})

    @api.depends('carrier_tracking_ref')
    def _compute_carrier_tracking_ref_barcode(self):
        for p in self:
            barcode = self.env['ir.actions.report'].barcode('Code128',p.carrier_tracking_ref, width=600, height=100, humanreadable=1)
            p.carrier_tracking_ref_barcode = base64.b64encode(barcode)
