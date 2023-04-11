# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID

def create_missing_journal_for_shop(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ecommerce.shop']._create_missing_journal()

class eCommerceShop(models.Model):
    _inherit = 'ecommerce.shop'

    #enable_accounting = fields.Boolean('Enable Accounting')

    journal_id = fields.Many2one('account.journal', 'Journal')
    _last_transaction_sync = fields.Datetime(readonly=True)

    @api.model
    def _create_missing_journal(self, company=None):
        company = company or self.env.user.company_id
        journals = self.env['account.journal']
        if company.chart_template_id:
            for shop in self.env['ecommerce.shop'].search([('state','=','auth'), ('journal_id', '=', False)]):
                shop.journal_id = self.env['account.journal'].create(shop._prepare_account_journal_vals(company))
                journals += shop.journal_id
        return journals

    @api.multi
    def _prepare_account_journal_vals(self, company):
        self.ensure_one()
        account_vals = company.chart_template_id._prepare_transfer_account_for_direct_creation(self.name, company)
        account = self.env['account.account'].create(account_vals)
        return {
            'name': self.name,
            'code': 'ECOM'[:(5-len(str(self.id)))] + str(self.id),
            'sequence': 999,
            'type': 'bank',
            'company_id': company.id,
            'default_debit_account_id': account.id,
            'default_credit_account_id': account.id,
        }

    @api.multi
    def write(self, vals):
        res = super(eCommerceShop, self).write(vals)
        for shop in self:
            if not shop.journal_id and shop.state == 'auth':
                shop.journal_id = self.env['account.journal'].create(shop._prepare_account_journal_vals(self.env.user.company_id))
        return res

    @api.model
    def cron_sync_transaction(self):
        self.env['ecommerce.shop'].search([('state','=','auth'),('auto_sync','=',True)]).sync_transaction()

    @api.multi
    def sync_transaction(self,**kw):
        for shop in self:
            getattr(shop, f'_sync_transaction_{shop.platform_id.platform}')(**kw)
