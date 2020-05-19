# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from datetime import datetime, timedelta, date
from odoo.tools.float_utils import float_round, float_compare, float_is_zero
import logging
_logger = logging.getLogger(__name__)

class eCommerceShop(models.Model):
    _inherit = 'ecommerce.shop'

    def _sync_transaction_lazada(self, **kw):
        self.ensure_one()
        kw.setdefault('limit', 500)
        kw.setdefault('offset', 0)
        kw.setdefault('start_time', self._last_transaction_sync and (self._last_transaction_sync + timedelta(days=1)).strftime("%Y-%m-%d") \
            or (date.today()-timedelta(days=7)).strftime("%Y-%m-%d"))
        if not kw['start_time'] < date.today().strftime("%Y-%m-%d") or not kw['start_time'] > self._last_transaction_sync.strftime("%Y-%m-%d"):
            return False
        dt = datetime.strptime(kw['start_time'],"%Y-%m-%d")
        kw.setdefault('end_time', (dt + timedelta(6-dt.weekday())).strftime("%Y-%m-%d"))
        transactions = []
        while True:
            resp = self._py_client_lazada_request('/finance/transaction/detail/get','GET', **kw)
            transactions += resp['data']
            if len(resp['data']) < kw['limit']:
                break
            kw['offset'] += kw['limit']
        def init_value(t):
            return {
                'date': datetime.strptime(t['transaction_date'], "%d %b %Y"),
                'name': t.get('order_no') or t.get('fee_name') or t['transaction_number'],
                'amount': float(t['amount']),
                'note': 'Transactions: {}'.format(t['transaction_number'])
                }
        if transactions:
            transactions.sort(key=lambda t: (datetime.strptime(t['transaction_date'], "%d %b %Y"), t.get('order_no','')))
            stmt = self.env['account.bank.statement'].search([
                ('journal_id','=', self.journal_id.id),
                ('name','=',transactions[0]['statement'])
            ], limit=1)
            if not stmt:
                stmt =self.env['account.bank.statement'].create({
                    'journal_id': self.journal_id.id,
                    'name': transactions[0]['statement'],
                    'date': datetime.strptime(transactions[0]['transaction_date'], "%d %b %Y")
                })
                #include payout
                last_stmt = self.env['account.bank.statement'].search([
                    ('journal_id','=', self.journal_id.id),
                    ('date','>=',stmt.date-timedelta(days=7)),
                    ('date','<',stmt.date)
                ], limit=1)
                resp = self._py_client_lazada_request('/finance/payout/status/get','GET', created_after=(stmt.date-timedelta(days=7)).strftime("%Y-%m-%d"))
                if resp['data'] and last_stmt and last_stmt.line_ids[-1].ref != resp['data'][0]['statement_number']:
                    last_stmt.write({
                        'line_ids': [(0, _, {
                            'date': datetime.strptime(resp['data'][0]['created_at'], "%Y-%m-%d %H:%M:%S"),
                            'name': 'Payout: {}'.format(resp['data'][0]['statement_number']),
                            'amount': -float(resp['data'][0]['closing_balance']),
                        })]
                    })
                    last_stmt.balance_end_real = last_stmt.balance_end
                stmt.balance_start = last_stmt and last_stmt.balance_end or 0 
            lines, l = [], init_value(transactions[0])
            for t in transactions[1:]:
                if t.get('order_no') == l['name']:
                    l['amount'] += float(t['amount'])
                    l['note'] += ', {}'.format(t['transaction_number'])
                else:
                    lines.append(l)
                    l = init_value(t)
            lines.append(l)
            stmt.write({
                'line_ids': [(0, _, l) for l in lines],
            })
            stmt.balance_end_real = stmt.balance_end
            precision_digits = self.env['decimal.precision'].precision_get('Product Price')
            account_rcv = self.env['account.account'].search([('user_type_id.type', '=', 'receivable')], limit=1)
            for line in stmt.line_ids.sorted(key=lambda r: r.id)[-len(lines):]:
                order = self.env['sale.order'].search([
                    ('ecommerce_shop_id','=', self.id),
                    ('client_order_ref','=',line.name),
                    ('state','in',['sale','done'])], limit=1)
                if not order:
                    continue
                if any([i.state == 'paid' for i in order.invoice_ids]):
                    order.write({
                        'order_line': [(0, _, {
                            'product_id': self.env.ref('connector_ecommerce_common_account.product_product_ecommerce_expense').id,
                            'product_uom_qty': 1,
                            'qty_delivered': 1,
                            'price_unit': line.amount
                        })]
                    })
                elif float_compare(line.amount, order.amount_untaxed, precision_digits=precision_digits) != 0:
                    order.write({
                        'order_line': [(0, _, {
                            'product_id': self.env.ref('connector_ecommerce_common_account.product_product_ecommerce_expense').id,
                            'product_uom_qty': 1,
                            'qty_delivered': 1,
                            'price_unit': line.amount - order.amount_untaxed
                        })]
                    })
                if order.invoice_status == 'to invoice':
                    order.invoice_ids.filtered(lambda i: i.state == 'draft').unlink()
                    invoice_ids = order.action_invoice_create(final=True)
                for invoice in order.invoice_ids:
                    invoice.reference = order.client_order_ref
                    if invoice.state == "draft": invoice.action_invoice_open()
                counterpart_aml_dicts = []
                for ml in self.env['account.move.line'].search([
                    ('account_id','=',line.partner_id and line.partner_id.property_account_receivable_id.id or account_rcv.id),
                    ('invoice_id','in', order.invoice_ids.ids),
                    ('move_id.state','=','posted'),
                ]):
                    amount = ml.currency_id and ml.amount_residual_currency or ml.amount_residual
                    if amount == 0: 
                        continue
                    counterpart_aml_dicts.append({
                        'move_line': ml,
                        'name': ml.name,
                        'debit': amount < 0 and -amount or 0,
                        'credit': amount > 0 and amount or 0,
                    })
                line.process_reconciliation(counterpart_aml_dicts=counterpart_aml_dicts)
            self._last_transaction_sync = l['date']
            


