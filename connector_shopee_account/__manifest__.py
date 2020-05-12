# -*- coding: utf-8 -*-
{
    'name': "connector_shopee_account",

    'summary': """
        Connector between shopee api and odoo accounting""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Que Nguyen",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'E-commerce',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['connector_ecommerce_common_account', 'connector_shopee'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
