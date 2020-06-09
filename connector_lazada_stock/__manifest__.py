# -*- coding: utf-8 -*-
{
    'name': "connector_lazada_stock",

    'summary': """
        Connect Lazada API to control stock operation""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Que Nguyen",
    'website': "http://scaleup.top",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['connector_ecommerce_common_stock', 'connector_lazada'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/stock_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
