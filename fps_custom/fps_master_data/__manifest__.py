
{
    'name': 'FPS: Master Data Governance',
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
        'views/product_inherit_views.xml',
     ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
