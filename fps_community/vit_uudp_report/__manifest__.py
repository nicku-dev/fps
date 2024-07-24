# -*- coding: utf-8 -*-
{
    'name' : 'Custom UUDP Report',
    'version' : '2.0',
    'summary': 'Custom report for uudp',
    'sequence': 16,
    'category': 'Extra Tools',
    'description': """
Custom UUDP Report
=====================================
uudp report that will generate a pdf report, which user choose.
    """,
    'category': 'Accounting',
    'website': 'http://vitraining.com/',
    'images' : [],
    'depends' : ['base_setup', 'report', 'sale', 'vit_uudp', 'account'],
    'data': [
        'wizard/parsial_report_view.xml',
        'wizard/once_report_view.xml',
        'wizard/summary_report_view.xml',
        'views/vit_uudp_report_parsial.xml',
        'views/report_parsial.xml',
        'views/vit_uudp_report_once.xml',
        'views/report_once.xml',

    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
