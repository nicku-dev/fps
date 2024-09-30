
{
    'name': 'FPS: Purchase Flow',
    'category': 'LKT/Freight',
    'version': '16.0.1.0.0',
    'summary': 'Freight Management Services untuk PT FPS',
    'description': 'Module for Managing Purchase and Costing in Freight Operations',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['base', 'product', 'account', 'fps_fms' ,'purchase',],
    'images': [
        'static/description/icon.png',
        ],
        
    'data': [
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}