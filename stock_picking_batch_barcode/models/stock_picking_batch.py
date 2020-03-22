# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class StockPickingBatch(models.Model):
    _name = 'stock.picking.batch'
    _inherit = ['stock.picking.batch','barcodes.barcode_events_mixin']

    alert = fields.Integer()
    message_type = fields.Selection([
        ('info', 'Barcode read with additional info'),
        ('error', 'No barcode found'),
        ('more_match', 'More than one match found'),
        ('success', 'Barcode read correctly'),
    ], readonly=True)
    message = fields.Char(readonly=True)
    
    def _set_message_info(self, type, message, barcode):
        """
        Set message type and message description.
        For manual entry mode barcode is not set so is not displayed
        """
        self.message_type = type
        if barcode:
            self.message = _('Tracking barcode: %s (%s)') % (barcode, message)
        else:
            self.message = '%s' % message 

    def on_barcode_scanned(self, barcode):
        pickings = self.picking_ids.filtered(lambda p: p.carrier_tracking_ref == barcode)
        _logger.info(pickings)
        if pickings:
            if len(pickings) > 1:
                self._set_message_info('more_match',_('More than one picking found'), barcode)
            #val = {'picking_ids': [(1, p.id, {'process_datetime': fields.Datetime.now()}) for p in pickings]}
            #val = {'picking_ids': [(4, p.id, _) for p in pickings]}
            #self.update(val)
            for p in pickings:
                for move in pickings.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                    for move_line in move.move_line_ids:
                        move_line.qty_done = move_line.product_uom_qty
            else:
                self._set_message_info('success', _('Barcode read correctly'), barcode)
        else:
            self._set_message_info('error',_('No available picking found'), barcode)

        self.alert=1
   
    def print_delivery(self):
        pickings = self.mapped('picking_ids')
        if not pickings:
            raise UserError(_('Nothing to print.'))
        return self.env.ref('stock.action_report_delivery').report_action(pickings)

#    @api.onchange('picking_ids')
#    def onchange_picking_ids(self):
#        res = {'value':{
#            'picking_ids': [
#                (1, p.id, {'process_datetime': fields.Datetime.now()}) for p in self.picking_ids.filtered(lambda r: r.process_datetime == False)
#                ]}}
#        return res

