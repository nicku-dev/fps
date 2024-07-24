
{
    'name': 'FPS: Freight Management System',
    'category': 'LKT/Freight',
    'version': '16.0.1.0.0',
    'summary': 'Freight Management Services untk PT FPS',
    'description': 'Module for Managing All Frieght Operations',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['base', 'product', 'account', 'sale', 'fleet'],
    'images': [
        'static/description/icon.png',
        ],
    'data': [
        'data/freight.port.csv',
        'data/freight.load.csv',
        'views/freight_load.xml',
        'data/freight_order_type.xml',
        'data/freight.port.csv',
        'views/freight_order.xml',
        'views/freight_order_type.xml',
        'views/freight_port.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
        'data/freight_order_data.xml',
        ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
