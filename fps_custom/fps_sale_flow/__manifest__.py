
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
    'depends': ['base', 'fps_freight_order', 'account', 'sale', 'fleet'],
    'images': [
        'static/description/icon.png',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'reports/so_report.xml',
        'views/sale_menus_inherit.xml',
        # 'wizard/custom_revision.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
