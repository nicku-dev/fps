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

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
import datetime
from odoo.addons.terbilang import terbilang

class PencairanWizard(models.TransientModel):
    _inherit = 'pencairan.wizard'

    @api.multi
    def _get_default_journal(self):
        if self.env.context.get('active_id',False) :
            cair = self.env['uudp.pencairan'].browse(self.env.context.get('active_id'))
            if cair.journal_id2:
                return cair.journal_id2.id

    @api.multi
    def _get_default_company(self):
        if self.env.context.get('active_id',False) :
            cair = self.env['uudp.pencairan'].browse(self.env.context.get('active_id'))
            if cair.company_id:
                return cair.company_id.id


    journal_interco_id = fields.Many2one('account.journal', string='Journal Interco',)# default=_get_default_journal)
    company_id = fields.Many2one("res.company", string="Company", default=_get_default_company)


    # def action_pencairan(self):
    #     #import pdb;pdb.set_trace()
    #     res = super(PencairanWizard, self).action_pencairan()
    #     if res and self.journal_interco_id :
    #         if not res.journal_id.update_posted:
    #             res.journal_id.write({'update_posted':True})
    #             res.button_cancel()
    #             res.journal_id.write({'update_posted':False})
    #         else :
    #             res.button_cancel()
    #         # search kode akun interco di company form pencairan dibuat
    #         account = self.env['account.account'].sudo()
    #         coa_interco = account.search([('code','=',self.journal_interco_id.account_interco_credit_id.code),('company_id','=',res.company_id.id)],limit=1)
    #         if not coa_interco :
    #             raise UserError(_('Account dengan kode %s tidak ada di company % !') % (self.journal_interco_id.account_interco_credit_id.code, res.company_id.name ) )

    #         #for line in res.line_ids.filtered(lambda x: x.credit != 0.0) :
    #         for line in res.line_ids :
    #             if line.credit != 0.0 :
    #                 line.write({'account_id'    : coa_interco.id, 
    #                             'partner_id'    : res.company_id.partner_id.id, })
    #                             #'name'          : coa_interco.name })
    #                 line.move_id.write({'ref'   : res.uudp_pencairan_id.name,
    #                                     'narration'  : res.uudp_pencairan_id.notes })
    #         label_debit = self.notes
    #         if not label_debit :
    #             label_debit = self.journal_interco_id.account_interco_debit_id.name
    #         # create jurnal interco di company sebelah
    #         account_move_line = []
    #         #account debit
    #         account_move_line.append((0, 0 ,{'account_id'       : self.journal_interco_id.account_interco_debit_id.id, 
    #                                         'partner_id'        : res.company_id.partner_id.id, 
    #                                         'analytic_account_id' : self.uudp_pencairan_id.ajuan_id.department_id.analytic_account_id.id,
    #                                         'name'              : label_debit, 
    #                                         'debit'             : self.nominal, 
    #                                         'company_id'        : self.journal_interco_id.company_id.id,
    #                                         'date_maturity'     : self.date})) #, 'analytic_account_id':self.uudp_pencairan_id.ajuan_id.department_id.analytic_account_id.id  

                                                     
    #         #account credit
    #         account_move_line.append((0, 0 ,{'account_id'       : self.journal_interco_id.default_credit_account_id.id, 
    #                                         'partner_id'        : False, 
    #                                         'analytic_account_id' : self.uudp_pencairan_id.ajuan_id.department_id.analytic_account_id.id,
    #                                         'name'              : self.journal_interco_id.default_credit_account_id.name, 
    #                                         'credit'            : self.nominal, 
    #                                         'company_id'        : self.journal_interco_id.company_id.id,
    #                                         'date_maturity'     : self.date})) #, 'analytic_account_id':self.uudp_pencairan_id.ajuan_id.department_id.analytic_account_id.id
    #         #create journal entry
    #         data = {"uudp_pencairan_id"      : self.uudp_pencairan_id.id,
    #                               "journal_id"          : self.journal_interco_id.id,
    #                               "ref"                 : self.uudp_pencairan_id.name,
    #                               "date"                : self.date,
    #                               "company_id"          : self.journal_interco_id.company_id.id,
    #                               "terbilang"           : terbilang.terbilang(int(round(self.nominal,0)), "IDR", "id"),
    #                               "line_ids"            : account_move_line,
    #                               "narration"           : res.uudp_pencairan_id.notes}
    #         interco_entires = self.env['account.move'].create(data)
    #         interco_entires.post()

    #     return res.post()


PencairanWizard()