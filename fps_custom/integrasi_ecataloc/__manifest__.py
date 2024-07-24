{
    'name': 'FPS: Integrasi Ecataloc',
    'category': 'LKT/Freight',
    'version': '16.0.1.0.0',
    'summary': 'Integrasi dengan ecatalo',
    'description': 'Module ini dibuat untuk melengkapi penarikan data dan juga penyesuaian odoo FPS dengan E-Cataloc penyesuaian Field, FLow, Relasi, dan Juga Flag/tag dll.',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['base','contact'],
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
