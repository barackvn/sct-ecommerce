# -*- coding: utf-8 -*-
{
    'name': "connector_ecommerce_common_account",

    'summary': """
        Connect eCommerce API to Odoo account invoice and payment""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Que Nguyen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'eCommerce',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['connector_ecommerce_common', 'hr_expense'],

    # always loaded
    'data': [
        'data/product_data.xml',
        'data/cron.xml',
        'views/ecommerce_shop_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'post_init_hook': 'create_missing_journal_for_shop',
    'demo': [
        'demo/demo.xml',
    ],
}
