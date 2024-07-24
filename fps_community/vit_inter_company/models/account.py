# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018  ADHOC SA  (http://www.vitraining.com)
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
from collections import defaultdict
import math
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ['ir.needaction_mixin','mail.thread','account.move.line']

    name = fields.Char(required=True, string="Label", track_visibility='onchange')
    debit = fields.Monetary(default=0.0, currency_field='company_currency_id', track_visibility='onchange')
    credit = fields.Monetary(default=0.0, currency_field='company_currency_id', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict', track_visibility='onchange')
    account_id = fields.Many2one('account.account', string='Account', required=True, index=True,
        ondelete="cascade", domain=[('deprecated', '=', False)], default=lambda self: self._context.get('account_id', False), track_visibility='onchange')
    partner_name = fields.Char('Partner Name')


    @api.model
    def create(self, vals):
        partner = self.env['res.partner']
        # import pdb;pdb.set_trace()
        if vals.get('partner_name', False) and not vals.get('partner_id', False):
            new_partner = partner.sudo().search([('ref','=',vals['partner_name'])], limit=1)
            if not new_partner :
                new_partner = partner.sudo().search([('name','=',vals['partner_name'])], limit=1)
            if new_partner :
                vals['partner_id'] = new_partner.id
        if not vals.get('company_id', False):
          vals['company_id'] = self.env.user.company_id.id
        return super(AccountMoveLine, self).create(vals)

    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        # handle jika partner di move_line kosong
        if self.filtered(lambda j: j.partner_id) :
            line_id = self.filtered(lambda j: j.partner_id)[0]
            for rec in self :
                for line in rec.filtered(lambda j: not j.partner_id and j.account_id.internal_type in ('receivable', 'payable')):
                    line.update({'partner_id':line_id.partner_id.id})
        return super(AccountMoveLine, self).reconcile(writeoff_acc_id=writeoff_acc_id, writeoff_journal_id=writeoff_journal_id)

AccountMoveLine()


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['ir.needaction_mixin','mail.thread','account.move']

    @api.multi
    def _get_default_journal(self):
        if self.env.context.get('default_journal_type'):
            return self.env['account.journal'].search([('type', '=', self.env.context['default_journal_type'])], limit=1).id

    ref = fields.Char(string='Reference', copy=False, track_visibility='onchange')
    date = fields.Date(required=True, states={'posted': [('readonly', True)]}, index=True, default=fields.Date.context_today, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'posted': [('readonly', True)]}, default=_get_default_journal, track_visibility='onchange')
    state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted')], string='Status',
      required=True, readonly=True, copy=False, default='draft',
      help='All manually created new journal entries are usually in the status \'Unposted\', '
           'but you can set the option to skip that status on the related journal. '
           'In that case, they will behave as journal entries automatically created by the '
           'system on document validation (invoices, bank statements...) and will be created '
           'in \'Posted\' status.', track_visibility='onchange')
    narration = fields.Text(string='Internal Note', track_visibility='onchange')

    @api.multi
    def button_cancel(self):
        self.write({'state': 'draft'})
        res = super(AccountMove, self).button_cancel()
        return res


AccountMove()


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    show_on_journal_entries = fields.Boolean('Show on journal entries', help='Centang jika ingin muncul di journal enries')
    interco_journal = fields.Boolean('Interco Journal', help='Journal Khusus Inter Company')
    account_interco_debit_id = fields.Many2one("account.account","Interco Debit Account")
    account_interco_credit_id = fields.Many2one("account.account","Interco Credit Account")
    mdr_fee = fields.Float("MDR Fee (%)")
    mdr_account_id = fields.Many2one("account.account", "MDR Account")
    active = fields.Boolean("Active", default=True)

    @api.model
    def create(self, vals):
        acc = self.env['account.account']
        if 'default_credit_account_id' in vals :
            account = acc.browse(vals['default_credit_account_id'])
            new_account = acc.sudo().search([('code','=',account.code),('company_id','=',vals['company_id'])])
            if new_account :
                vals['default_credit_account_id'] = new_account.id
        if 'default_debit_account_id' in vals :
            account = acc.browse(vals['default_debit_account_id'])
            new_account = acc.sudo().search([('code','=',account.code),('company_id','=',vals['company_id'])])
            if new_account :
                vals['default_debit_account_id'] = new_account.id
        return super(AccountJournal, self).create(vals)


AccountJournal()


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    journal_interco_id = fields.Many2one('account.journal', 'Interco Journal')
    account_interco_id = fields.Many2one('account.account', 'Interco Account')
    notes_interco      = fields.Char('Interco Notes')
    partner_id2        = fields.Many2one('res.partner','Partner 2')

    @api.onchange('journal_id')
    def onchange_journal_id(self):
      if self.invoice_ids :
        return {'domain': {'journal_id':[('company_id','=',self.invoice_ids[0].company_id.id)]}}

    @api.onchange('journal_interco_id')
    def onchange_journal_interco_id(self):
      account = self.env["account.account"].sudo()
      if self.payment_type == 'outbound' :
        self.account_interco_id = self.journal_interco_id.account_interco_debit_id.id
      elif self.payment_type == 'inbound' :
        self.account_interco_id = self.journal_interco_id.account_interco_credit_id.id

    @api.onchange('account_interco_id')
    def onchange_account_interco_id(self):
      if self.payment_type == 'outbound' :
        return {'domain': {'account_interco_id':[('id','=',self.journal_interco_id.account_interco_credit_id.id)]}}
      if self.payment_type == 'inbound' :
        return {'domain': {'account_interco_id':[('id','=',self.journal_interco_id.account_interco_debit_id.id)]}}

    @api.onchange('account_id')
    def onchange_account_id(self):
      if self.payment_type == 'outbound' :
        return {'domain': {'account_interco_id':[('id','=',self.journal_id.account_interco_credit_id.id)]}}
      if self.payment_type == 'inbound' :
        return {'domain': {'account_interco_id':[('id','=',self.journal_id.account_interco_debit_id.id)]}}

    @api.multi
    def post(self):
      res = super(AccountPayment, self).post()
      #import pdb;pdb.set_trace()
      if self.partner_id2 :
        account = False
        if self.payment_type == 'inbound':
          account = self.journal_id.default_credit_account_id
        elif self.payment_type == 'outbound':
          account = self.journal_id.default_debit_account_id
        if account and self.move_line_ids:
          # allow cancel journal dulu dan balikin lagi
          if not self.move_line_ids[0].move_id.journal_id.update_posted:
            self.move_line_ids[0].move_id.journal_id.write({'update_posted':True})
            self.move_line_ids[0].move_id.button_cancel()
          for line in self.move_line_ids :
            if line.account_id.id == account.id :
              line.update({'partner_id' : self.partner_id2.id})
          #self.move_line_ids[0].move_id.journal_id.write({'update_posted':False})
          self.move_line_ids[0].move_id.post()
      if self.journal_interco_id and self.invoice_ids :
        ref = False
        if self.notes_interco :
          ref = self.notes_interco
        invoice = self.invoice_ids[0]
        payment = invoice.payment_ids.sorted(key=lambda inv: -inv.id)[0] # cari id terbaru saja
        lines = []
        # Vendor bills
        if self.payment_type == 'outbound' :
          credit_line = payment.move_line_ids.filtered(lambda i: i.debit == 0.0 )
          if credit_line :
            # allow cancel journal dulu dan balikin lagi
            if not credit_line[0].move_id.journal_id.update_posted:
              credit_line[0].move_id.journal_id.write({'update_posted':True})
              credit_line[0].move_id.button_cancel()
              credit_line[0].update({'account_id' : self.journal_id.account_interco_credit_id.id})
              #credit_line[0].move_id.journal_id.write({'update_posted':False})
            else :
              credit_line[0].move_id.button_cancel()
              credit_line[0].update({'account_id' : self.journal_id.account_interco_credit_id.id})
            credit_line[0].move_id.post()
            if not ref :
              ref = self.journal_interco_id.account_interco_credit_id.name
            datas_line = (0, 0,{'name'          : ref,
                            'partner_id'        : False,
                            'account_id'        : self.journal_interco_id.default_credit_account_id.id,
                            'credit'            : self.amount ,
                            'debit'             : 0.0,
                            'payment_id'        : payment.id,
                            'company_id'        : self.journal_interco_id.company_id.id,
                        })
            lines.append(datas_line)
            datas_line2 = (0, 0,{'name'         : ref,
                            'partner_id'        : self.company_id.partner_id and self.company_id.partner_id.id or False,
                            'account_id'        : self.journal_interco_id.account_interco_debit_id.id,
                            'credit'            : 0.0,
                            'debit'             : self.amount,
                            'payment_id'        : payment.id,
                            'company_id'        : self.journal_interco_id.company_id.id,
                        })
            lines.append(datas_line2)
        # Customer bills
        elif self.payment_type == 'inbound' :
          debit_line = payment.move_line_ids.filtered(lambda i: i.credit == 0.0 )
          if debit_line :
            # allow cancel journal dulu dan balikin lagi
            if not debit_line[0].move_id.journal_id.update_posted:
              debit_line[0].move_id.journal_id.write({'update_posted':True})
              debit_line[0].move_id.button_cancel()
              debit_line[0].update({'account_id' : self.journal_id.account_interco_debit_id.id})
              #debit_line[0].move_id.journal_id.write({'update_posted':False})
            else :
              debit_line[0].move_id.button_cancel()
              debit_line[0].update({'account_id' : self.journal_id.account_interco_debit_id.id})
            debit_line[0].move_id.post()
            if not ref :
              ref = self.journal_interco_id.account_interco_debit_id.name
            datas_line = (0, 0,{'name'          : ref,
                            'partner_id'        : self.company_id.partner_id and self.company_id.partner_id.id or False,
                            'account_id'        : self.journal_interco_id.account_interco_credit_id.id,
                            'credit'            : self.amount ,
                            'debit'             : 0.0,
                            'payment_id'        : payment.id,
                            'company_id'        : self.journal_interco_id.company_id.id,
                        })
            lines.append(datas_line)
            datas_line2 = (0, 0,{'name'         : ref,
                            'partner_id'        : False,
                            'account_id'        : self.journal_interco_id.default_debit_account_id.id,
                            'credit'            : 0.0,
                            'debit'             : self.amount,
                            'payment_id'        : payment.id,
                            'company_id'        : self.journal_interco_id.company_id.id,
                        })
            lines.append(datas_line2)
        
        if lines :
            datas = {'ref'              : self.move_line_ids[0].move_id.ref or False,
                    'journal_id'        : self.journal_interco_id.id,
                    'date'              : self.payment_date,
                    'company_id'        : self.journal_interco_id.company_id.id,
                    'line_ids'          : lines}
            account_move = self.env["account.move"]
            journal_interco = account_move.create(datas)
            info = "Journal Inter Company "+ str(self.journal_interco_id.company_id.name)+" Created.."
            print info
            # journal_interco.post()
            # extra_info = "Journal Inter Company "+ str(self.company_interco_id.name) +" Posted"
            # print extra_info

      return res

AccountPayment()


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    code = fields.Char("Reference", required=True)

    @api.model
    def create(self, vals):
        code = vals.get('code', False)
        if code :
            code_exist = self.sudo().search([('code','=',code)])
            if code_exist :
                raise UserError(_('Reference/code already exist'))
        return super(AccountAnalyticAccount, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'code' in vals :
            code_exist = self.sudo().search([('code', '=', vals['code'])])
            if code_exist:
                raise UserError(_('Reference/code already exist'))
        return super(AccountAnalyticAccount, self).write(vals)


AccountAnalyticAccount()