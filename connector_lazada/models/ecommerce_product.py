#-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class LazadaProductSample(models.Model):
    _name = 'lazada.product.sample'
    _inherit = 'ecommerce.product.sample'

    product_tmpl_ids = fields.One2many('product.template', 'lazada_product_sample_id', readonly=True)
    short_description = fields.Html()
    warranty_type = fields.Char(string=_("Warranty Type"))
    warranty = fields.Char(string=_("Warranty Period"))
    product_warranty = fields.Char(string=_("Warranty Policy"))
    package_weight = fields.Float(string=_("Package Weight (kg)"))
    package_length = fields.Float(string=_("Package Lenghth (cm)"))
    package_width = fields.Float(string=_("Package Width (cm)"))
    package_height = fields.Float(string=_("Package Height (cm)"))
    package_content = fields.Char(string=_("What's in the box"))
    Hazmat = fields.Char(string=_("Hazmat"))
    video = fields.Char(string=_("Video URL"))
    categ_attribute_ids = fields.One2many('ecommerce.product.sample.attribute.line', 'lazada_sample_id')

class LazadaProductSampleAttributeLine(models.Model):
    _inherit = 'ecommerce.product.sample.attribute.line'

    lazada_sample_id = fields.Many2one('lazada.product.sample', string='Product Sample', ondelete='cascade', required=True)

class LazadaProductTemplate(models.Model):
    _inherit = 'ecommerce.product.template'

    
