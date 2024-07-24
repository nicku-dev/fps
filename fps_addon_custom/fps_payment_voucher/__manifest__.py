
{
    'name': 'Pengajuan Dana dan Reimburse',
    'version': '16.0.1.0.0',
    'category': 'LKT/Freight',
    'summary': 'Module ini berfungsi mengatur Uang yang di Pertanggung Jawabkan',
    'description': """
        Module for Managing All Payment Voucher Operations
            * Pengajuan dana
            * REIMBURSE
            * Pencairan dana / reimberse
            * Penyelesaian / pertanggungjawaban dana
            * Tidak ada jurnal terkait bank / cash
    """,
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['base', 
                'product', 
                'account', 
                'hr',
                'hr_expense',
                'sale',
                'fleet'
                ],
    'images': [
        'static/description/icon.png',
        ],
    'data': [
        "data/fps_payment_voucher_data.xml",
        'views/payment_voucher.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
        ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}

