
{
    'name': 'FPS: Base Custom',
    'category': 'LKT/Freight',
    'version': '16.0.1.0.0',
    'summary': 'Freight Management Services untk PT FPS',
    'description': 'Module for Extend and Managing FPS BASE Module',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['base','contacts'],
    'images': [
        'static/description/icon.png',
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/sale.shipment.type.csv',
        'views/sale_order_view.xml',
        'reports/spal_report.xml',
        'views/sale_menus_inherit.xml',
        # 'wizard/custom_revision.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
