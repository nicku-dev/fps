
{
    'name': 'FPS: API E-cataloc',
    'category': 'LKT/API',
    'version': '16.0.1.0.0',
    'summary': 'Integrasi Ecataloc dengang Odoo untuk PT FPS',
    'description': 'Module for Managing API Communication between Odoo and Ecataloc',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['base', 'product', 'account','fps_freight_order'],
    'images': [
        'static/description/icon.png',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/api_bank_view.xml',
        'views/api_mdg_view.xml',
        'views/configuration_view.xml',
        'views/contact_view.xml',
        'views/menu.xml',
        'views/res_config_setting_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
