# -*- coding: utf-8 -*-
{
    'name': "connector_ecommerce_common",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale','sale_product_pack','delivery'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/ecommerce_config_views.xml',
        'views/ecommerce_product_views.xml',
        'views/ecommerce_shop_views.xml',
        'views/product_views.xml',
        'views/ecommerce_category_selector_views.xml',
        'wizard/ecommerce_product_preview_views.xml',
        'data/cron.xml',
        'data/ecommerce_product_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
