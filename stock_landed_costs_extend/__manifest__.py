# -*- coding: utf-8 -*-
{
    'name': "stock_landed_costs_extend",

    'summary': """
        Connect Landed Costs to Purchase and Expense module""",

    'description': """
        Automatically create Landed Cost when create Expense or Purchase with Landed Cost product.
        Allow to link Expense to Purchase.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_landed_costs','hr_expense','purchase_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_expense_views.xml',
        'views/purchase_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
