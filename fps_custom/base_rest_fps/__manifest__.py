# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "FPS: Base Rest API",
    'category': 'LKT/Freight',
    'version': '16.1.1.0.0',
    "summary": """
        FPS addon for Base REST API""",
    'description': 'Module for Extend and Managing All FPS S',
    'author': 'Nicku F. Pasaribu',
    "maintainers": ["Nicku Fritzie Pasaribu"],
    'company': 'Fangiono Perkasa Sejati',
    "development_status": "Beta",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/rest-framework",
    "depends": [
        "base_rest",
        "base_rest_datamodel",
        "base_rest_pydantic",
        "component",
        "extendable",
        "pydantic",
    ],
    "external_dependencies": {
        "python": ["jsondiff", "extendable-pydantic", "marshmallow", "pydantic>=2.0.0"]
    },
    "installable": True,
}
