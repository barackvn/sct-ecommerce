# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class StockPickingBatch(models.Model):
    _name = 'stock.picking.batch'
    _inherit = ['stock.picking.batch','barcodes.barcode_events_mixin']

    picking_type_id = fields.Many2one(
            'stock.picking.type', 'Operation Type',
            readonly=True,
            states={'draft': [('readonly', False)]})
    message_type = fields.Selection([
        ('info', 'Barcode read with additional info'),
        ('not_found', 'No barcode found'),
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
        self._set_message_info('success', _('Barcode read correctly'), barcode)
        pickings=self.env['stock.picking'].search([
            ('batch_id','=',False),
            ('state','not in',['done', 'cancel']),
            ('picking_type_id','=?',self.picking_type_id.id),
            ('carrier_tracking_ref','=',barcode)])
        _logger.info(pickings)
        if pickings:
            if len(pickings) > 1:
                self._set_message_info('more_match',_('More than one picking found'), barcode)
            val = {'picking_ids': [(1, p.id, {'process_datetime': fields.Datetime.now()}) for p in pickings]}
            #val = {'picking_ids': [(4, p.id, _) for p in pickings]}
            self.update(val)
        elif self.picking_type_id:
            self._set_message_info('not_found',_('No available picking in this operation type'), barcode)
        else:
            self._set_message_info('not_found',_('No available picking found'), barcode)
    
    @api.onchange('picking_ids')
    def onchange_picking_ids(self):
        res = {'value':{
            'picking_ids': [
                (1, p.id, {'process_datetime': fields.Datetime.now()}) for p in self.picking_ids.filtered(lambda r: r.process_datetime == False)
                ]}}
        return res

    @api.multi
    def remove_undone_pickings(self):
        self.mapped('active_picking_ids').write({'batch_id': False, 'process_datetime':False})
        self.verify_state()
