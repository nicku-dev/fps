
{
    'name': 'FPS: Payment Requisition',
    'version': '16.0.1.0.0',
    'category': 'LKT/Freight',
    'summary': 'Module ini berfungsi untuk pengajuan Uang yang di Pertanggung Jawabkan',
    'description': """
        Module for Managing All Payment Requisition Operations
            * Pengajuan dana
            * REIMBURSE
            * Pencairan dana 
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
                'fleet',
                'fps_fms',
                'analytic',
                ],
    'images': [
        'static/description/icon.png',
        ],
    'data': [
        'data/payment_requisition_data.xml',
        'views/payment_requisition_views.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
        ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}

