# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Expense(models.Model):
    _inherit = "hr.expense"

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order", readonly=True, states={'draft': [('readonly', False)], 'reported': [('readonly', False)]}, domain=[('state', '=', 'purchase')])

class ExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def approve_expense_sheets(self):
        super(ExpenseSheet, self).approve_expense_sheets()
        for sheet in self:
            for line in sheet.expense_line_ids:
                if line.product_id.landed_cost_ok and line.purchase_order_id:
                    if not line.purchase_order_id.landed_cost_id:
                        line.purchase_order_id.landed_cost_id = self.env['stock.landed.cost'].create({
                            'cost_lines': [(0, _, {
                                'product_id': line.product_id.id,
                                'name': line.name,
                                'split_method': line.product_id.split_method or 'equal',
                                'price_unit': line.unit_amount,
                                'account_id': line.product_id.property_account_expense_id.id or line.product_id.categ_id.property_account_expense_categ_id.id
                            })],
                            'picking_ids': [(6, _, line.purchase_order_id.picking_ids.filtered(lambda p: p.state == 'done').ids)],
                        })
                    elif line.purchase_order_id.landed_cost_id.state == 'draft': 
                        line.purchase_order_id.landed_cost_id.write({
                            'cost_lines': [(0, _, {
                                'product_id': line.product_id.id,
                                'name': line.name,
                                'split_method': line.product_id.split_method or 'equal',
                                'price_unit': line.unit_amount,
                                'account_id': line.product_id.property_account_expense_id.id or line.product_id.categ_id.property_account_expense_categ_id.id
                            })],
                        })
                    if (
                        all(
                            x.state in ['done', 'cancel']
                            for x in line.purchase_order_id.picking_ids
                        )
                        and line.purchase_order_id.landed_cost_id.state == 'draft'
                    ):
                        line.purchase_order_id.landed_cost_id.compute_landed_cost()
                        line.purchase_order_id.landed_cost_id.button_validate()

    
