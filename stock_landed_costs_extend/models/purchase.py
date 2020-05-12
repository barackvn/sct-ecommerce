# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    landed_cost_id = fields.Many2one('stock.landed.cost', string='Landed Cost')
    expense_ids = fields.One2many('hr.expense', 'purchase_order_id', string='Expenses')
    expense_count = fields.Integer("# of Expenses", compute='_compute_expense_count', compute_sudo=True)

    @api.multi
    @api.depends('expense_ids')
    def _compute_expense_count(self):
        expense_data = self.env['hr.expense'].read_group([('purchase_order_id', 'in', self.ids), ('state', '=', 'done')], ['purchase_order_id'], ['purchase_order_id'])
        mapped_data = dict([(item['purchase_order_id'][0], item['purchase_order_id_count']) for item in expense_data])
        for purchase_order in self:
            purchase_order.expense_count = mapped_data.get(purchase_order.id, 0)

    def button_approve(self, force=False):
        result = super(PurchaseOrder, self).button_approve(force=force)
        for order in self:
            if not order.landed_cost_id:
                landed_cost_lines = order.order_line.filtered('product_id.landed_cost_ok')
                if landed_cost_lines:
                    order.landed_cost_id = self.env['stock.landed.cost'].create({
                        'cost_lines': [(0, _, {
                            'product_id': l.product_id.id,
                            'name': l.name,
                            'split_method': l.product_id.split_method or 'equal',
                            'price_unit': l.price_unit,
                            'account_id': l.product_id.property_account_expense_id.id or l.product_id.categ_id.property_account_expense_categ_id.id
                        }) for l in landed_cost_lines],
                    })
        return result

    def button_cancel(self):
        result = super(PurchaseOrder, self).button_cancel()
        for order in self:
            if order.landed_cost_id:
                order.landed_cost_id.button_cancel()
                order.landed_cost_id = False
