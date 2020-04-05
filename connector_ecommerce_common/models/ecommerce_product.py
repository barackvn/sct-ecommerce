# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, tools
import babel
from odoo.exceptions import UserError
from odoo.tools import pycompat
import datetime
from werkzeug import urls
import functools

import dateutil.relativedelta as relativedelta
import logging
_logger = logging.getLogger(__name__)


def format_date(env, date, pattern=False):
    if not date:
        return ''
    try:
        return tools.format_date(env, date, date_format=pattern)
    except babel.core.UnknownLocaleError:
        return date


def format_tz(env, dt, tz=False, format=False):
    record_user_timestamp = env.user.sudo().with_context(tz=tz or env.user.sudo().tz or 'UTC')
    timestamp = fields.Datetime.from_string(dt)

    ts = fields.Datetime.context_timestamp(record_user_timestamp, timestamp)

    # Babel allows to format datetime in a specific language without change locale
    # So month 1 = January in English, and janvier in French
    # Be aware that the default value for format is 'medium', instead of 'short'
    #     medium:  Jan 5, 2016, 10:20:31 PM |   5 janv. 2016 22:20:31
    #     short:   1/5/16, 10:20 PM         |   5/01/16 22:20
    if env.context.get('use_babel'):
        # Formatting available here : http://babel.pocoo.org/en/latest/dates.html#date-fields
        from babel.dates import format_datetime
        return format_datetime(ts, format or 'medium', locale=env.context.get("lang") or 'en_US')

    if format:
        return pycompat.text_type(ts.strftime(format))
    else:
        lang = env.context.get("lang")
        langs = env['res.lang']
        if lang:
            langs = env['res.lang'].search([("code", "=", lang)])
        format_date = langs.date_format or '%B-%d-%Y'
        format_time = langs.time_format or '%I-%M %p'

        fdate = pycompat.text_type(ts.strftime(format_date))
        ftime = pycompat.text_type(ts.strftime(format_time))
        return u"%s %s%s" % (fdate, ftime, (u' (%s)' % tz) if tz else u'')

def format_amount(env, amount, currency):
    fmt = "%.{0}f".format(currency.decimal_places)
    lang = env['res.lang']._lang_get(env.context.get('lang') or 'en_US')

    formatted_amount = lang.format(fmt, currency.round(amount), grouping=True, monetary=True)\
        .replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')

    pre = post = u''
    if currency.position == 'before':
        pre = u'{symbol}\N{NO-BREAK SPACE}'.format(symbol=currency.symbol or '')
    else:
        post = u'\N{NO-BREAK SPACE}{symbol}'.format(symbol=currency.symbol or '')

    return u'{pre}{0}{post}'.format(formatted_amount, pre=pre, post=post)

try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': urls.url_quote,
        'urlencode': urls.url_encode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': functools.reduce,
        'map': map,
        'round': round,

        # dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently.
        'relativedelta': lambda *a, **kw : relativedelta.relativedelta(*a, **kw),
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")

class eCommerceProductSample(models.AbstractModel):
    _name = 'ecommerce.product.sample'

    ecomm_categ_selector_id= fields.Many2one('ecommerce.category.selector')
    name = fields.Char()
    ecomm_categ_id = fields.Many2one('ecommerce.category', related='ecomm_categ_selector_id.ecomm_categ_id', store=True)
    platform_id = fields.Many2one('ecommerce.platform', required=True)
    product_tmpl_ids = fields.One2many('product.template', 'ecomm_product_sample_id', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', ondelete='cascade', store=True,
            compute='_compute_product_tmpl_id', inverse='_inverse_product_tmpl_id')
    ecomm_attribute_lines = fields.One2many('ecommerce.product.sample.attribute.line', 'res_id', 'Category Attributes', 
            auto_join=True, domain = lambda self: [('res_model','=', self._name)])
    ecomm_product_image_ids = fields.One2many('ecommerce.product.image', 'res_id', 'Images', 
            auto_join=True, domain = lambda self: [('res_model','=',self._name)])

    _sql_constraints = [
            ('platform_product_unique', 'unique(platform_id, product_tmpl_id)','This product sample already exists in this platform')
            ]

    @api.depends('product_tmpl_ids')
    def _compute_product_tmpl_id(self):
        for s in self:
            s.product_tmpl_id = s.product_tmpl_ids and s.product_tmpl_ids[0]

    def _inverse_product_tmpl_id(self):
        for s in self:
            s.product_tmpl_ids = (s.product_tmpl_id)

    def unlink(self):
        self = self.exists()
        self.mapped('ecomm_attribute_lines').unlink()
        self.mapped('ecomm_product_image_ids').unlink()
        return super(eCommerceProductSample, self).unlink()

    @api.onchange('ecomm_categ_id')
    def onchange_ecomm_categ_id(self):
        getattr(self, '_onchange_ecomm_categ_id_{}'.format(self.platform_id.platform))()

class eCommerceProductTemplate(models.Model):
    _name = 'ecommerce.product.template'
    _description = "eCommerce Product"

    name = fields.Char()
    description = fields.Text()
    t_name = fields.Char()
    t_description = fields.Text()
    sku = fields.Char()
    shop_id = fields.Many2one('ecommerce.shop', required=True)
    platform_id = fields.Many2one('ecommerce.platform', related="shop_id.platform_id", store=True)
    platform_item_idn = fields.Char(string=_("ID Number"),index=True)
    product_tmpl_id = fields.Many2one('product.template')
    product_product_id = fields.Many2one('product.product', string=_("Single Variant"))
    ecomm_product_product_ids = fields.One2many('ecommerce.product.product', 'ecomm_product_tmpl_id', string=_("Variants"))
    carrier_ids = fields.One2many('ecommerce.product.carrier', 'ecomm_product_tmpl_id', auto_join=True, string=_('Delivery Methods'))
    #add_image_ids = fields.One2many('ir.attachment', 'res_id',
    #        domain= lambda self: [('res_model', '=', self._name),('mimetype', 'ilike', 'image')],
    #        string='Add Images')
    ecomm_product_image_ids = fields.One2many('ecommerce.product.image', 'res_id', string=_("Images"),
            auto_join=True, domain = [('res_model','=','ecommerce.product.template')])
    auto_update_stock = fields.Boolean()
    has_sample = fields.Boolean(compute='compute_has_sample')
    _last_info_update = fields.Datetime(string=_("Info Updated On"))
    _last_sync = fields.Datetime(strong=_("Last Sync"))
    #_sync_res = fields.Selection([('fail',_("Fail")),('success',_("Success"))], string=_("Sync Result"))

    model_object_field = fields.Many2one('ir.model.fields', string="Field")
    sub_object = fields.Many2one('ir.model', 'Sub-model', readonly=True,
                                 help="When a relationship field is selected as first field, "
                                      "this field shows the document model the relationship goes to.")
    sub_model_object_field = fields.Many2one('ir.model.fields', 'Sub-field',
                                             help="When a relationship field is selected as first field, "
                                                  "this field lets you select the target field within the "
                                                  "destination document model (sub-model).")
    null_value = fields.Char('Default Value', help="Optional value to use if the target field is empty")
    copy_value = fields.Char('Placeholder Expression', help="Final placeholder expression, to be copy-pasted in the desired template field.")
    lang = fields.Char('Language',
                       help="Optional translation language (ISO code) to select when sending out an email. "
                            "If not set, the english version will be used. "
                            "This should usually be a placeholder expression "
                            "that provides the appropriate language, e.g. "
                            "${object.partner_id.lang}.",
                       placeholder="${object.partner_id.lang}")
    
    def build_expression(self, field_name, sub_field_name, null_value):
        expression = ''
        if field_name:
            expression = "${object." + field_name
            if sub_field_name:
                expression += "." + sub_field_name
            if null_value:
                expression += " or '''%s'''" % null_value
            expression += "}"
        return expression

    @api.onchange('model_object_field', 'sub_model_object_field', 'null_value')
    def onchange_sub_model_object_value_field(self):
        if self.model_object_field:
            if self.model_object_field.ttype in ['many2one', 'one2many', 'many2many']:
                model = self.env['ir.model']._get(self.model_object_field.relation)
                if model:
                    self.sub_object = model.id
                    self.copy_value = self.build_expression(self.model_object_field.name, self.sub_model_object_field and self.sub_model_object_field.name or False, self.null_value or False)
            else:
                self.sub_object = False
                self.sub_model_object_field = False
                self.copy_value = self.build_expression(self.model_object_field.name, False, self.null_value or False)
        else:
            self.sub_object = False
            self.copy_value = False
            self.sub_model_object_field = False
            self.null_value = False

    def _render_template(self, template_txt):
        self.ensure_one()
        try:
            template = mako_template_env.from_string(tools.ustr(template_txt))
        except Exception:
            _logger.info("Failed to load template %r", template_txt, exc_info=True)
            raise UserError(_("Failed to load template %r")% template)

        # prepare template variables
        variables = {
            'format_date': lambda date, format=False, context=self._context: format_date(self.env, date, format),
            'format_tz': lambda dt, tz=False, format=False, context=self._context: format_tz(self.env, dt, tz, format),
            'format_amount': lambda amount, currency, context=self._context: format_amount(self.env, amount, currency),
            'user': self.env.user,
            'ctx': self._context,  # context kw would clash with mako internals
        }
        variables['object'] = self
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.info("Failed to render template %r using values %r" % (template, variables), exc_info=True)
            raise UserError(_("Failed to render template %r using values %r")% (template, variables))

        return render_result

    def get_template(self):
        self.ensure_one()
        lang =  self._render_template(self.lang)
        if lang:
            template = self.with_context(lang=lang)
        else:
            template = self
        return template

    def generate_values(self, fields=None):
        self.ensure_one()
        if fields is None: 
            fields = ['t_name','t_description']
        template = self.get_template()
        
        return {field[2:]: template._render_template(getattr(template, field)) for field in fields}

    def preview(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "ecommerce.product.preview",
            "views": [[False, "form"]],
            "res_id": self.env['ecommerce.product.preview'].create(self.generate_values()).id,
            "target": "new",
        }

    def update_info(self, vals={}, image=False):
        for p in self:
            if image: getattr(p, '_update_image_{}'.format(p.platform_id.platform))()
            getattr(p, "_update_info_{}".format(p.platform_id.platform))(vals=vals)

    def add_to_shop(self, val={}):
        for p in self:
            getattr(p, '_add_to_shop_{}'.format(p.platform_id.platform))(vals=vals)

    def update_stock(self):
        platform_id = self.mapped('platform_id')
        platform_id.ensure_one()
        getattr(self, "_update_stock_{}".format(platform_id.platform))()

    @api.model
    def cron_update_stock(self):
        for shop in self.env['ecommerce.shop'].search([('auto_sync','=',True)]):
            self.env['ecommerce.product.template'].search([('shop_id','=', shop.id),('auto_update_stock','=',True)]).update_stock()

    def match_sku(self):
        for item in self:
            if item.ecomm_product_product_ids.filtered('sku'):
                item.product_product_id = False
                if item.product_tmpl_id:
                    d = {}
                    for v in item.ecomm_product_product_ids:
                        if v.sku:
                            d.update({v: self.env['product.product'].search([
                                ('product_tmpl_id','=',item.product_tmpl_id.id),
                                ('default_code','=',v.sku)])[:1].id
                            })
                    if all(d.values()):
                        for v in d:
                            v.write({'product_product_id': d[v]})
                    else:
                        item.write({
                            'product_tmpl_id': False,
                            'ecomm_product_product_ids': [(1, v.id, {'product_product_id': False}) for v in item.ecomm_product_product_ids]
                        })
                else:
                    item.product_tmpl_id = self.env['product.template'].search([
                        ('product_variant_ids.default_code','in',[v.sku]) for v in item.ecomm_product_product_ids if v.sku
                    ])[:1]
                    item.write({
                        'ecomm_product_product_ids': [(1, v.id, {
                            'product_product_id': self.env['product.product'].search([
                                ('product_tmpl_id','=',item.product_tmpl_id.id),
                                ('default_code','=',v.sku)
                            ])[:1].id}) for v in item.ecomm_product_product_ids if v.sku]
                        })
            elif item.sku:
                if not item.product_product_id or item.product_product_id.default_code != item.sku:
                    p = self.env['product.product'].search([
                        ('default_code','=',item.sku)])
                    item.write({
                        'product_product_id': p and p[0].id,
                        'product_tmpl_id': p and p[0].product_tmpl_id.id
                    })
            else:
                item.write({
                    'product_tmpl_id': False,
                    'product_product_id': False,
                    'ecomm_product_product_ids': [(1, p.id, {'product_product_id': False}) for p in item.ecomm_product_product_ids]
                })

    @api.onchange('product_tmpl_id', 'product_product_id')
    def onchange_product_id(self):
        if self.platform_id:
            getattr(self, '_onchange_product_id_{}'.format(self.platform_id.platform))()
        elif self._context.get('platform'):
            getattr(self, '_onchange_product_id_{}'.format(self._context.get('platform')))()

    @api.onchange('shop_id')
    def onchange_shop_id(self):
        if self.shop_id:
            getattr(self, '_onchange_shop_id_{}'.format(self.platform_id.platform))()

    @api.onchange()
    def load_demo_value(self):
        self.ensure_one()
        sample = self.product_tmpl_id and self.product_tmpl_id.mapped('{}_product_sample_id'.format(self.platform_id.platform))
        if not sample: return
        
        return {'value':{
            'name': self.ecomm_product_sample_id.name,
            'description': self.ecomm_product_sample_id.description,
            'ecomm_product_image_ids': [(5, _,_)] + [(0, _,{
                'res_model': 'ecommerce.product.template',
                'image_url': i.image_url,
            }) for i in sample.ecomm_product_image_ids]
        }}

    @api.depends('product_tmpl_id', 'platform_id')
    def compute_has_sample(self):
        for i in self:
            if i.product_tmpl_id and i.platform_id and i.product_tmpl_id.mapped('{}_product_sample_id'.format(i.platform_id.platform)): 
                i.has_sample = True
            else:
                i.has_sample = False


class eCommerceProductProduct(models.Model):
    _name = 'ecommerce.product.product'
    _description = "eCommerce Product Variant"

    name = fields.Char()
    platform_variant_idn = fields.Char(index=True, readonly=True)
    product_product_id = fields.Many2one('product.product', domain=lambda self: ['product_tmpl_id','=',self.ecomm_product_tmpl_id])
    ecomm_product_tmpl_id = fields.Many2one('ecommerce.product.template', ondelete='cascade', required=True)
    sku = fields.Char()

    @api.onchange(product_product_id)
    def onchange_product_product_id(self):
        if not self.platform_variant_idn: self.sku = self.product_product_id.default_code




class eCommerceProductImage(models.Model):
    _name = 'ecommerce.product.image'
    _description = 'eCommerce Product Image'
    _order = 'sequence'

    sequence = fields.Integer()
    name = fields.Char('Name')
    image_id = fields.Many2one('ir.attachment','Image Attachment')
    image_url = fields.Char('Image Url', compute='compute_image_url', inverse='inverse_image_url', store=True)
    image_url_view = fields.Char('Image', related='image_url')
    image = fields.Binary('Image', attachment=True)
    res_id = fields.Integer()
    res_model = fields.Char()
    res_field = fields.Char()

    #ecomm_product_tmpl_id = fields.Many2one('ecommerce.product.template','Related Product')

    @api.depends('image')
    def compute_image_url(self):
        for i in self:
            i.image_id = self.env['ir.attachment'].search([
                ('res_model','=','ecommerce.product.image'),
                ('res_id','=',i.id),
                ('res_field', '=', 'image')])[:1]
            if i.image_id:
                i.image_url = self.env['ir.config_parameter'].get_param('web.base.url') + i.image_id.local_url

    def inverse_image_url(self):
        for i in self:
            i.image_id = False
            i.image = False

    def refresh(self):
        return

#    @api.onchange('image_url')
#    def onchange_image_url(self):
#        self.image_url_view = self.image_url
