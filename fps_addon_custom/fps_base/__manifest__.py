
{
    'name': 'FPS: Base Custom',
    'category': 'LKT/Freight',
    'version': '16.0.1.0.0',
    'summary': 'Extend Module untuk PT FPS',
    'description': 'Module for Extend and Managing FPS BASE Module',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['base','contacts','sale'],
    'images': [
        'static/description/icon.png',
        ],
    'data': [
        "data/ir_config_parameter_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_inherit_view.xml",
        "views/sale_order.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
