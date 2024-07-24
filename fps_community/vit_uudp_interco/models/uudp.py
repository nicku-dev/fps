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


class UUDP(models.Model):
    _inherit = 'uudp'
    _order = "name desc"

    @api.onchange('by_pass_selisih')
    def onchange_by_pass_selisih(self):
        if self.diff_interco:
            self.diff_interco = False
            self.difference = False
            self.difference_notes = False
            self.journal_difference_id = False


    @api.onchange('diff_interco')
    def onchange_diff_interco(self):
        if self.diff_interco:
            self.difference = False
            self.difference_notes = False
            self.by_pass_selisih = False
        else :
            self.journal_difference_id = False

    def _default_journal(self):
        return False
        # return self.env.context.get('default_journal_id') or self.env['account.journal'].search([('name', 'ilike', 'Miscellaneous Operation'),
        #                                                                                       ('company_id','=',self.env['res.company']._company_default_get().id)], limit=1)


    journal_difference_id = fields.Many2one('account.journal', string='Interco Journal', track_visibility='onchange')
    diff_interco = fields.Boolean('Difference Inter Company')
    user_id = fields.Many2one("res.users", string="Employee", default=lambda self: self.env.user, store=True, required=True, 
        track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(string="Date", required=True, default=fields.Datetime.now, track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)]})
    ajuan_id = fields.Many2one('uudp', string="Ajuan", domain="[('type','=','pengajuan')]",readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one("account.journal", string="Journal", required=False, track_visibility='onchange', default=_default_journal)
    coa_kredit = fields.Many2one("account.account", string="Credit Account", related="journal_id.default_credit_account_id", store=True)
    journal_entry_id = fields.Many2one("account.move", string="Journal Entry",readonly=True, states={'draft': [('readonly', False)]})
    difference = fields.Many2one("account.account", string="Difference Account",readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env['res.company']._company_default_get(), required=True,readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one("hr.department", string="Department", track_visibility='onchange', domain="[('company_id','=',company_id)]")

    @api.multi
    def action_see_uudp_entries(self):
        self.ensure_one()
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain' : [('ref', 'ilike', '%'+self.name+'%')],
            'context': {},
            'target': 'current',
        }

    def prepare_move_line_interco(self, account, partner_id, name, debit, credit, date, company_id):
        move_line = (0, 0, {'account_id'        : account.id,
                            'partner_id'        : partner_id,
                            'name'              : name, 
                            'debit'             : debit,
                            'credit'            : credit,
                            'date_maturity'     : date,
                            'company_id'        : company_id.id})
        return move_line

    def prepare_move_interco(self, journal, name, date, company_id, notes, account_move_line):
        move = {"journal_id"    : journal.id,
                  "ref"         : name,
                  "date"        : date,
                  "company_id"  : company_id.id,
                  "narration"   : notes,
                  "line_ids"    : account_move_line}
        return move

    ####################### Tutup pembuatan journal ##############################
    # @api.multi
    # def button_confirm_finance(self):
    #     if self.uudp_ids:
    #         account = self.env['account.account'].sudo()
    #         for s in self.uudp_ids:
    #             if not s.product_id :
    #                 raise UserError(_('Product dengan deskripsi %s belum di set!')%(s.description))
    #             # if self.type == 'penyelesaian' and self.sisa_penyelesaian > 0.0 and not self.difference:
    #             #     raise UserError(_('Jika ada sisa penyelesaian, difference account harus diisi !'))
    #             elif s.product_id.property_account_expense_id:
    #                 uudp_account = account.sudo().search([('code','=',s.product_id.property_account_expense_id.code),
    #                                                         ('company_id','=',self.company_id.id)],limit=1)
    #                 if not uudp_account :
    #                     raise UserError(_('Tidak ditemukan kode CoA %s pada company %s !') % (s.product_id.property_account_expense_id.code,self.company_id.name))
    #                 self.write({'coa_debit': uudp_account.id})
    #             elif s.product_id.categ_id.property_account_creditor_price_difference_categ:
    #                 uudp_account = account.search([('code','=',s.product_id.categ_id.property_account_creditor_price_difference_categ.code),
    #                                                 ('company_id','=',self.company_id.id)],limit=1)
    #                 if not uudp_account :
    #                     raise UserError(_('Tidak ditemukan kode CoA %s pada company %s !') % (s.product_id.categ_id.property_account_creditor_price_difference_categ.code,self.company_id.name))
    #                 self.write({'coa_debit': uudp_account.id})
    #             else:
    #                 raise UserError(_('Account atas deskipsi %s belum di set!')%(s.description))
    #         self.write_state_line('confirm_finance')
    #         self.post_mesages_uudp('Confirmed by Finance')
    #         return self.write({'state' : 'confirm_finance'})
    #     raise AccessError(_('Pengajuan masih kosong') )


    @api.multi
    def button_confirm_finance_interco(self):
        # move_obj = self.env['account.move']
        # if self.type != 'pengajuan':
        #     account = self.env['account.account'].sudo()
        #     partner = False
        #     if self.type == 'penyelesaian':
        #         partner = self.ajuan_id.responsible_id.partner_id.id
        #     else:
        #         partner = self.responsible_id.partner_id.id

        #     if not self.journal_id or not self.coa_kredit :
        #          raise UserError(_('Pada tab other info, Journal dan Account Credit harus diisi !'))

        #     now = datetime.datetime.now()
        #     total_ajuan = 0
        #     account_move_line = []
        #     if self.uudp_ids:
        #         #import pdb;pdb.set_trace()
        #         total_debit = 0
        #         for s in self.uudp_ids:
        #             if s.product_id.property_account_expense_id:
        #                 coa_debit_product = s.product_id.property_account_expense_id
        #                 s.write({'coa_debit': coa_debit_product.id})
        #             elif s.product_id.categ_id.property_account_creditor_price_difference_categ:
        #                 coa_debit_product = s.product_id.categ_id.property_account_creditor_price_difference_categ
        #                 s.write({'coa_debit': coa_debit_product.id})
        #             else:
        #                 raise UserError(_('Account atas product %s belum di set!')%(s.product_id.name))

        #             if s.journal_id:
        #                 if not s.journal_id.account_interco_debit_id :
        #                     raise UserError(_('Account default interco (debit) %s belum di set!')%(s.journal_id.name))
        #                 else :
        #                     # search kode akun interco di company form pencairan dibuat
        #                     coa_interco = account.search([('code','=',s.journal_id.account_interco_debit_id.code),
        #                                                 ('company_id','=',self.company_id.id)],limit=1)
        #                     if not coa_interco :
        #                         raise UserError(_('Account inter company dengan kode %s tidak ada di company % !') % (s.journal_id.account_interco_debit_id.code, self.company_id.name ) )
        #                     s.write({'coa_debit': coa_interco.id})
        #                     # search coa product di company interco
        #                     coa_debit_product_interco = account.search([('code','=',coa_debit_product.code),
        #                                                                 ('company_id','=',s.journal_id.company_id.id)],limit=1)
        #                     if not coa_debit_product_interco :
        #                         raise UserError(_('Account inter company dengan kode %s tidak ada di company % !') % (coa_debit_product.code, s.journal_id.company_id.name ) )
        #                     partner = s.journal_id.company_id.partner_id.id
        #                     # create jurnal interco
        #                     lines_interco = []
        #                     # debit
        #                     lines_interco.append(self.prepare_move_line_interco(coa_debit_product_interco, partner, s.operating_unit_id.id, coa_debit_product_interco.name, s.total, 0.0, self.date, s.journal_id.company_id ))
        #                     # credit
        #                     lines_interco.append(self.prepare_move_line_interco(s.journal_id.account_interco_credit_id, self.company_id.partner_id.id, False, s.journal_id.account_interco_credit_id.name, 0.0, s.total, self.date, s.journal_id.company_id ))
        #                     # jika selisih dibebankan ke intecompany

        #                     interco_journal = self.prepare_move_interco(s.journal_id, self.name, self.date, s.journal_id.company_id, self.notes, lines_interco)
        #                     int_journal = move_obj.create(interco_journal)
        #                     int_journal.post()

        #             account_move_line.append(self.prepare_move_line_interco(s.coa_debit, partner, s.operating_unit_id.id or False, s.description, s.total, 0.0, self.date, s.coa_debit.company_id ))

        #             total_debit += s.total                             

        #         if self.type == 'penyelesaian':
        #             if total_debit < self.total_ajuan and not self.difference and not self.journal_difference_id:
        #                 raise AccessError(_('Nilai penyelesaian kurang dari nilai ajuan \n Silahkan isi Difference Account untuk memasukan selisih ke journal entry'))
        #             # jika masuk selisih masuk ke company yg mengeluarkan
        #             elif total_debit < self.total_ajuan and self.difference and not self.diff_interco:
        #                 selisih = self.total_ajuan - total_debit
        #                 account_different = self.difference
        #                 account_move_line.append(self.prepare_move_line_interco(account_different, False, False, account_different.name, selisih, 0.0, self.date, account_different.company_id))
        #             # jika selisih dimasukan ke company lain, maka create jurnal interco
        #             elif total_debit < self.total_ajuan and self.journal_difference_id and self.diff_interco:
        #                 selisih = self.total_ajuan - total_debit
        #                 # search kode akun interco di company form pencairan dibuat
        #                 coa_diff_interco = account.search([('code','=',self.journal_difference_id.account_interco_debit_id.code),('company_id','=',self.company_id.id)],limit=1)
        #                 if not coa_diff_interco :
        #                     raise UserError(_('Account difference inter company dengan kode %s tidak ada di company % !') % (coa_diff_interco.account_interco_debit_id.code, self.company_id.name ) )
        #                 account_different = coa_diff_interco
        #                 account_move_line.append(self.prepare_move_line_interco(account_different, self.journal_difference_id.company_id.partner_id.id, False, account_different.name, selisih, 0.0, self.date, account_different.company_id))
        #                 # create jurnal selisih interco
        #                 interco_selisih = []
        #                 # debit bank
        #                 interco_selisih.append(self.prepare_move_line_interco(self.journal_difference_id.default_debit_account_id, self.journal_difference_id.company_id.partner_id.id, False, self.journal_difference_id.default_debit_account_id.name, selisih, 0.0, self.date, self.journal_difference_id.company_id))
        #                 # debit
        #                 interco_selisih.append(self.prepare_move_line_interco(self.journal_difference_id.account_interco_credit_id, self.company_id.partner_id.id, False, self.journal_difference_id.account_interco_credit_id.name, 0.0, selisih, self.date, self.journal_difference_id.company_id))
        #                 #create journal entry selisih
        #                 data_selisih = self.prepare_move_interco(self.journal_difference_id, self.name, self.date, self.journal_difference_id.company_id, self.notes, interco_selisih)

        #                 journal_selisih = move_obj.create(data_selisih)
        #                 journal_selisih.post()

        #         #account credit
        #         account_move_line.append(self.prepare_move_line_interco(self.coa_kredit, partner, False, self.coa_kredit.name, 0.0, self.total_ajuan, self.date, self.company_id))
        #         #create journal entry
        #         data = self.prepare_move_interco(self.journal_id, self.name, self.date, self.company_id, self.notes, account_move_line)

        #         journal_entry = move_obj.create(data)
        #         if journal_entry:
        #             journal_entry.post()
        #             self.write_state_line('done')
        #             self.ajuan_id.write({'selesai':True})
        #             self.post_mesages_uudp('Done')
        #             return self.write({'state' : 'done', 'journal_entry_id':journal_entry.id})
        #         else:
        #             raise AccessError(_('Gagal membuat journal entry') )
        # else:
        if self.uudp_ids:
            self.write_state_line('confirm_finance')
            self.post_mesages_uudp('Confirmed by Finance')
            return self.write({'state' : 'confirm_finance'})
        raise AccessError(_('Pengajuan masih kosong') )

    # @api.multi
    # def button_done_finance(self):
    ####################### Tutup pembuatan journal ##############################
    #     if self.type == 'penyelesaian' and not self.diff_interco:
    #         res = super(UUDP, self).button_done_finance()
    #     elif self.type == 'penyelesaian' and self.diff_interco:
    #         move_obj = self.env['account.move']
    #         account = self.env['account.account'].sudo()
    #         partner = self.ajuan_id.responsible_id.partner_id.id

    #         # if not self.journal_id :
    #         #      raise UserError(_('Pada tab other info, Journal harus diisi !'))

    #         total_ajuan = 0
    #         now = datetime.datetime.now()
    #         total_ajuan = self.total_ajuan
    #         if self.uudp_ids:
    #             account_move_line = []

    #             # sql = "SELECT account_account.name, udel.coa_debit, udel.description, SUM(udel.total) AS total FROM uudp_detail AS udel INNER JOIN uudp ON uudp.id = udel.uudp_id INNER JOIN account_account ON udel.coa_debit = account_account.id WHERE udel.uudp_id=%s GROUP BY udel.coa_debit, account_account.name, udel.description"

    #             # cr = self.env.cr
    #             # cr.execute(sql, ([(self.id)]))
    #             # result = self.env.cr.dictfetchall()
    #             total_debit = 0.0
                
    #             ajuan_total = 0.0
    #             journal_interco_created = False
    #             for ajuan in self.uudp_ids:
    #                 if not ajuan.coa_debit:
    #                     raise UserError(_('Account atas %s belum di set!')%(ajuan.description))
    #                 if ajuan.partner_id :
    #                     partner = ajuan.partner_id.id
    #                 tag_id = False
    #                 if ajuan.store_id :
    #                     tag_id = [(6, 0, [ajuan.store_id.account_analytic_tag_id.id])]
    #                 ajuan_total = ajuan.sub_total
    #                 #account debit
    #                 if ajuan.sub_total > 0.0 : 
    #                     account_move_line.append((0, 0 ,{'account_id'       : ajuan.coa_debit.id,
    #                                                      'partner_id'       : partner, 
    #                                                      'analytic_tag_ids' : tag_id,
    #                                                      'name'             : self.notes, 
    #                                                      'analytic_account_id':self.department_id.analytic_account_id.id,
    #                                                      'company_id'       : self.company_id.id,
    #                                                      'debit'            : ajuan_total, 
    #                                                      'date_maturity'    : self.date})) #,
    #                 elif ajuan.sub_total < 0.0 :
    #                     account_move_line.append((0, 0 ,{'account_id'       : ajuan.coa_debit.id,
    #                                                      'partner_id'       : partner, 
    #                                                      'analytic_tag_ids' : tag_id,
    #                                                      'name'             : self.notes, 
    #                                                      'analytic_account_id':self.department_id.analytic_account_id.id,
    #                                                      'company_id'       : self.company_id.id,
    #                                                      'credit'           : -ajuan_total, 
    #                                                      'date_maturity'    : self.date})) #,
    #                 total_debit += ajuan_total        
    #             if total_debit < total_ajuan :
    #                 # search kode akun interco di company form pencairan dibuat
    #                 coa_diff_interco = account.search([('code','=',self.journal_difference_id.account_interco_debit_id.code),('company_id','=',self.company_id.id)],limit=1)
    #                 if not coa_diff_interco :
    #                     raise UserError(_('Account difference inter company dengan kode %s tidak ada di company % !') % (coa_diff_interco.account_interco_debit_id.code, self.company_id.name ) )

    #                 selisih = total_ajuan - total_debit
    #                 account_move_line.append((0, 0 ,{'account_id'       : coa_diff_interco.id, # account piutang interco 
    #                                                 'partner_id'        : self.journal_difference_id.company_id.partner_id.id, 
    #                                                 'analytic_account_id':self.department_id.analytic_account_id.id,
    #                                                 'name'              : self.difference_notes, 
    #                                                 'company_id'        : self.company_id.id,
    #                                                 'debit'             : selisih, 
    #                                                 'date_maturity'     : self.date})) #, 
    #                 # create interco journal
    #                 if not journal_interco_created :
    #                     journal_interco_line = []
    #                     # debit bank interco
    #                     account_debt_interco = self.journal_difference_id.default_debit_account_id
    #                     partner_id = self.journal_difference_id.company_id.partner_id.id
    #                     name = self.difference_notes
    #                     # debit
    #                     journal_interco_line.append(self.prepare_move_line_interco(account_debt_interco, partner_id, self.journal_difference_id.default_debit_account_id.name, selisih, 0.0, self.date, self.journal_difference_id.company_id))
    #                     # credit
    #                     account_cred_interco = self.journal_difference_id.account_interco_credit_id
    #                     journal_interco_line.append(self.prepare_move_line_interco(account_cred_interco, self.company_id.partner_id.id, name, 0.0, selisih, self.date, self.journal_difference_id.company_id))
    #                     #create journal entry selisih
    #                     journal_interco = self.prepare_move_interco(self.journal_difference_id, self.name, self.date, self.journal_difference_id.company_id, self.notes, journal_interco_line)

    #                     journal_interco_created = move_obj.create(journal_interco)
    #                     journal_interco_created.post()
    #             #account credit
    #             account_move_line.append((0, 0 ,{'account_id' : self.ajuan_id.coa_debit.id, 
    #                                             'partner_id': partner, 
    #                                             'analytic_account_id':self.department_id.analytic_account_id.id,
    #                                             'name' : self.notes, 
    #                                             'credit' : total_ajuan, 
    #                                             'company_id':self.company_id.id,
    #                                             'date_maturity':self.date})) #, 
    #             #create journal entry
                
    #             journal_id = self.ajuan_id.pencairan_id.journal_id
    #             data={"journal_id":journal_id.id,
    #                   "ref":self.name,
    #                   "date":self.date,
    #                   "narration" : self.notes,
    #                   "company_id":self.company_id.id,
    #                   "line_ids":account_move_line,}
    #             journal_entry = self.env['account.move'].create(data)
    #             if journal_entry:
    #                 journal_entry.post()
    #                 self.write_state_line('done')
    #                 self.ajuan_id.write({'selesai':True})
    #                 self.post_mesages_uudp('Done')
    #                 return self.write({'state' : 'done', 'journal_entry_id':journal_entry.id})
    #         else:
    #             raise AccessError(_('Gagal membuat journal entry') )
    #         return self.write({'state' : 'done'})


    @api.multi
    def button_confirm(self):
        res = super(UUDP, self).button_confirm()
        if self.type == 'reimberse' and not self.uudp_ids : 
            raise AccessError(_('Detail pengajuan reimberse harus diisi !') )
        return res

UUDP()


class UUDPPencairan(models.Model):
    _inherit = 'uudp.pencairan'

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            self.journal_id = False
            self.coa_kredit = False
            self.journal_id2 = False
            self.journal_difference_id = False
            self.uudp_ids = False

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, track_visibility='onchange')
    coa_kredit = fields.Many2one("account.account", string="Bank Account", related="journal_id.default_credit_account_id", store=True)
    journal_id2 = fields.Many2one('account.journal', string='Interco Journal', track_visibility='onchange')
    company_id2 = fields.Many2one("res.company", string="Company Journal", related="journal_id2.company_id", store=True)

    ####################### Tutup pembuatan journal ##############################
    # @api.multi
    # def button_done_once(self):
    #     bank_account = self.coa_kredit
    #     if self.journal_id2 :
    #         # search kode akun interco di company form pencairan dibuat
    #         account = self.env['account.account'].sudo()
    #         coa_interco = account.search([('code','=',self.journal_id2.account_interco_credit_id.code),('company_id','=',self.company_id.id)],limit=1)
    #         if not coa_interco :
    #             raise UserError(_('Account dengan kode %s tidak ada di company % !') % (self.coa_kredit.code, self.company_id.name ) )
    #         self.write({'coa_kredit' : coa_interco.id})
    #         res = super(UUDPPencairan, self).button_done_once()
    #         # kembalikan ke semula
    #         self.write({'coa_kredit' : bank_account.id})
    #         journals = self.env['account.move'].search([('ref','ilike','%'+self.name+'%')])
    #         if journals :
    #             # buat jurnal interco di company lawan nya
    #             for j_lines in journals :
    #                 lines = []
    #                 for lines_interco in j_lines.line_ids :#self.journal_entry_id.line_ids :
    #                     tag_id = False
    #                     if lines_interco.analytic_tag_ids :
    #                         tag_id = [(6, 0, [tag.id for tag in lines_interco.analytic_tag_ids])]
    #                     # jika coa UUDP maka di interco company lawanya isi dg hutang interco
    #                     if lines_interco.credit == 0.0 :
    #                         debit =(0, 0, {'account_id'         : self.journal_id2.account_interco_debit_id.id,
    #                                         'partner_id'        : self.company_id.partner_id.id,
    #                                         'analytic_account_id' : lines_interco.analytic_account_id.id,
    #                                         'analytic_tag_ids'  : tag_id,
    #                                         'name'              : lines_interco.name, 
    #                                         'debit'             : lines_interco.debit,
    #                                         'credit'            : 0.0,
    #                                         'date_maturity'     : lines_interco.date_maturity,
    #                                         'company_id'        : self.company_id2.id})
    #                         lines.append(debit)
    #                         continue
    #                     else :
    #                         credit = (0, 0, {'account_id'       : self.journal_id2.default_credit_account_id.id,
    #                                         'partner_id'        : self.company_id2.partner_id.id,
    #                                          'analytic_account_id' : lines_interco.analytic_account_id.id ,
    #                                         'name'              : lines_interco.name, 
    #                                         'credit'            : lines_interco.credit,
    #                                         'debit'             : 0.0,
    #                                         'date_maturity'     : lines_interco.date_maturity,
    #                                         'company_id'        : self.company_id2.id})
    #                         lines.append(credit)

    #                         lines_interco.write({'partner_id' : self.company_id2.partner_id.id})
    #                 # import pdb;pdb.set_trace()
    #                 account_move = self.env["account.move"]
    #                 account_move_interco = account_move.create({'company_id' : self.company_id2.id,
    #                                                             'ref'       : j_lines.ref,
    #                                                             'date'      : self.tgl_pencairan,
    #                                                             'terbilang' : self.journal_entry_id.terbilang,
    #                                                             'journal_id': self.journal_id2.id,
    #                                                             #'analytic_account_id' : self.ajuan_id.department_id.analytic_account_id.id or False,
    #                                                             'line_ids'  : lines})

    #                 account_move_interco.post()

    #     else :
    #         res = super(UUDPPencairan, self).button_done_once()

    #     return res


    # @api.multi
    # def button_set_to_draft(self):
    #     for uudp in self.uudp_ids :
    #         uudp.write({'type_pencairan' : False,'state' : 'confirm_finance'})
    #     return super(UUDPPencairan, self).button_set_to_draft()


    @api.multi
    def action_see_uudp_pencairan_entries(self):
        self.ensure_one()
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain' : [('ref', 'ilike', '%'+self.name+'%')],
            'context': {},
            'target': 'current',
        }

UUDPPencairan()   


class uudpDetail(models.Model):
    _inherit = "uudp.detail"

    journal_id = fields.Many2one('account.journal', string='Journal Interco', track_visibility='onchange')

uudpDetail()