# -*- coding: utf-8 -*-

{
    'name': "FPS: Multi level Approval",
    'version': '16.0.2.0.0',
    'summary': """This module add the multiple approval option for invoice,
    			  bill,refund and credit notes.""",
    'description': """
    This module add the multiple approval option for 
    - invoice,
    - bill,
    - refund 
    - credit notes.
    
    """,
    'category': 'LKT/Freight',
    'author': 'Nicku F. Pasaribu',
    'maintainer': 'Lentera Kreasi Teknologi',
    'company': 'Fangiono Perkasa Sejati',
    'website': 'https://www.lenterateknologi.com',


    'depends': ['account'],
    'data': [
        'data/data.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/invoice_approval_view.xml',
        'views/menu.xml',
        'views/account_move_inherited.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'license': "AGPL-3",
}
