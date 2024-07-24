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
    "name": "Inter Company",
    "version": "2.1",
    "category": "Account",
    "sequence": 20,
    "author":  "vITraining",
    "website": "www.vitraining.com",
    "license": "AGPL-3",
    "summary": "",
    "description": """
    * filter jurnal_id di jurnal entry (tambah boolean di journal.journal) dan filter sesuai company

    * filter coa, operating unit, analityc account sesuai company

    * jika buat jurnal inter company otomatis create lawanya di company lain

    * transaksi inter co lewat cash & bank (bank statement)
    
    * bank statement ada boolean interco, company yang dituju dan account lawannya 

    * settingan CoA interco ada di master journal

    * untuk validate, reconcile, cancel, dan set to draft bank statement harus tambah group 'Allow Bank Statement Reconcile'

    * Tambah analytic account di bank statement yg update ke journal entries

    * Register payment bisa inter company

    * Jurnal entries bisa inter company

    * tambah analytic_tag_ids di addons/account/static/src/js/account_reconciliation_widgets.js --> keyword : 'Tambahan'

    * bisa hapus statement ketika sudah di reconcile (tambah tombol baru )
    """,
    "depends": [
        "base",
        "account",
        "account_cancel",
        "analytic",
        "vit_bank_statement_import",
    ],
    "data": [
        "views/account_view.xml",
        "views/account_bank_statement_view.xml",
        "views/partner_view.xml",
        "views/interco_entries_view.xml",
        "security/groups.xml",
        "data/data.xml",
    ],

    "demo": [
    ],

    "test": [
    ],

    "installable": True,
    "auto_install": False,
    "application": True,
}

