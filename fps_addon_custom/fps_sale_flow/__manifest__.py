
{
    'name': 'FPS: Sales Flow',
    'category': 'LKT/Freight',
    'version': '16.0.1.0.0',
    'summary': 'Freight Management Services untk PT FPS',
    'description': 'Module for Extend and Managing All FPS S',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['base', 'contacts', 'account', 'sale', 'fleet', 'fps_fms', 'sale_management','analytic',],
    'images': [
        'static/description/icon.png',
        ],
    'demo': [
        'data/sale_flow_demo.xml'
    ]
,    'data': [
        'views/sale_order_view.xml',
        'security/ir.model.access.csv',
        # 'views/sale_order_pricelist_view.xml',
        'data/sale.shipment.type.csv',
        'reports/spal_report.xml',
        'views/sale_menus_inherit.xml',
        # 'wizard/custom_revision.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
