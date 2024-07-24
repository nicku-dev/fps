# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018  Odoo SA  (http://www.vitraining.com)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "UUDP Inter Company",
    "version": "1.0",
    "category": "Extra Tools",
    "sequence": 20,
    "author":  "vITraining",
    "website": "www.vitraining.com",
    "license": "AGPL-3",
    "summary": "",
    "description": """
    * Multi Company Journal Pencairan dan Penyelesaian UUDP
    * Tidak ada jurnal interco
    """,
    "depends": [
        "base",
        "account",
        "hr",
        "vit_uudp",
        "vit_inter_company",
    ],
    "data": [
        "wizard/pencairan_view.xml",
        "views/uudp_view.xml",
    ],

    "demo": [
    ],

    "test": [
    ],

    "installable": True,
    "auto_install": False,
    "application": True,
}

