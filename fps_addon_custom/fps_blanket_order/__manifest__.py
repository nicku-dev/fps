
{
    'name': 'FPS: Blanket Order',
    'category': 'LKT/Freight',
    'version': '16.0.1.0.0',
    'summary': 'Menambah Fungsional Blanket Order sebagai contract kerja antara PT FPS dengan customer',
    'description': 'Module for Managing All Frieght Operations',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['base', 'sale', 'sale_blanket_order'],
    'images': [
        'static/description/icon.png',
        ],
    'data': [
        'views/sale_blanket_order_views.xml',
        ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
