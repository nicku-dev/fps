{
    'name': 'Auto Analytic Account and Plan',
    'category': 'LKT/Freight',
    'version': '1.0',
    'description': """
        Automatically creates an analytic account based on SO number and assigns a default analytic plan.
    """,
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',
    'depends': ['sale', 'account', 'analytic', 'fps_fms', 'account_accountant'],
    'data': [
        # 'views/sale_order.xml',
        'data/account.analytic.plan.csv',
        'views/analytic_plan.xml',
        'views/freight_order.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}