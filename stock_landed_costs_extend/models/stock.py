#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        if super(StockPicking, self).action_done():
            for p in self:
                if p.purchase_id and p.purchase_id.landed_cost_id:
                    p.purchase_id.landed_cost_id.write({
                        'picking_ids': [(4, p.id, _)]
                    })
                    if all([x.state in ['done', 'cancel'] for x in p.purchase_id.picking_ids]) and p.purchase_id.landed_cost_id.state == 'draft':
                        p.purchase_id.landed_cost_id.compute_landed_cost()
                        p.purchase_id.landed_cost_id.button_validate()
            return True
        else:
            return False


