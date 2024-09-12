# -*- coding: utf-8 -*-
{
    'name': "fps_account_flow",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    'images' : ['static/description/fps.png',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',      
        #'views/layouts.xml',
        'reports/kwitansi.xml',
        'reports/payment_voucher.xml',                
        #'views/views.xml',
        #'views/templates.xml',      
    ],

    'assets': {
        'web.assets_backend': [
            'fps_account_flow/static/src/css/fps.css'
        ]  
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
