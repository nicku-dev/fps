
{
    'name': 'FPS:  Freight Management System',
    'category': 'LKT/Freight',
    'version': '16.0.1.0.0',
    'summary': 'Freight Management Services untk PT FPS',
    'description': 'Module for Managing All Frieght Operations',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['base', 'product', 'account', 'sale'],
    'images': [
        # 'static/description/banner.png',
        'static/description/icon.png',
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/freight_order_data.xml',
        'views/freight_order.xml',
        'views/freight_port.xml',
        'views/freight_load.xml',
        'views/freight_container.xml',
        'views/custom_clearance.xml',
        'views/order_track.xml',
        'views/menu.xml',
        'report/report_order.xml',
        'report/report_tracking.xml',
        'report/report_tracking.xml',
        'wizard/custom_revision.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
     'email': "info@otibro.com", 'email': "info@otibro.com",
}
