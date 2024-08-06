{
    'name': 'Many2one Reference Field',
    'summary': """
        Many2one Reference Field
        """,
    'version': '0.0.1',
    'category': 'web,many2one',
    'author': 'La Jayuhni Yarsyah',
    'description': """
        Many2one reference fields
    """,
    
    'depends': [
        'web',
    ],
    # 'data': [
    #     'views/assets.xml',
    # ],

    'assets': {
        'web.assets_backend': [
            'static/src/xml/assets.xml',
        ],
        'web.assets_common': [
            'static/src/js/fields.js',
        ],
    },

    'installable': True,
    'auto_install': False,
    'application': True
}