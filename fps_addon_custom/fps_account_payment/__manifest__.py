# -*- coding: utf-8 -*-
{
    'name': "fps_account_payment",

    'summary': """
    Modul odoo ini dibuat untuk extend kebutuhan print out kwitansi dan fitur-fitur di modul akutansi lainya.
    1. Printout Kwitansi

""",

    'description': """
    Modul odoo ini dibuat untuk extend kebutuhan print out kwitansi dan fitur-fitur di modul akutansi lainya.
    1. Printout Kwitansi.

    """,

    'category': 'LKT/Freight',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['account'],
    'data': [
        # 'security/ir.model.access.csv',
        'reports/kwitansi_report.xml',

    ],
}
