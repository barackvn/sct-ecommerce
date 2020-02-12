# -*- coding: utf-8 -*-
{
    'name': "Stock Delivery Extend",

    'summary': """
        Delivery Tracking Reference as Barcode, Allow adding picking to batch by scanning Tracking Barcode""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Que Nguyen",
    'website': "http://www.scaleup.top",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['barcodes','stock_picking_batch_extended'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/stock_picking_batch_views.xml'
        #'views/views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
