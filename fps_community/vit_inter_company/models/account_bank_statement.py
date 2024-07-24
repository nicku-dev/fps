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

from odoo import api, fields, models, _
import time
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class AccountBankStatement(models.Model):
    _name = "account.bank.statement"
    _inherit = ['ir.needaction_mixin','mail.thread','account.bank.statement']

    @api.multi
    def check_confirm_bank(self):
        super(AccountBankStatement, self).check_confirm_bank()
        return {'type': 'ir.actions.client','tag': 'reload'}

    @api.model
    def create(self, vals):
        #import pdb;pdb.set_trace()  
        name = vals.get('name', False)
        if name == False :
            vals['name'] = self.env['ir.sequence'].next_by_code('account.bank.statement') or 'Statement'
        return super(AccountBankStatement, self).create(vals)

    @api.multi
    def _get_opening_balance(self, journal_id):
        last_bnk_stmt = self.search([('journal_id', '=', journal_id)], limit=1)
        if last_bnk_stmt:
            return last_bnk_stmt.balance_end
        return 0

    @api.multi
    def _set_opening_balance(self, journal_id):
        self.balance_start = self._get_opening_balance(journal_id)

    @api.model
    def _default_opening_balance(self):
        #Search last bank statement and set current opening balance as closing balance of previous one
        journal_id = self._context.get('default_journal_id', False) or self._context.get('journal_id', False)
        if journal_id:
            return self._get_opening_balance(journal_id)
        return 0

    @api.model
    def _default_journal(self):
        journal_type = self.env.context.get('journal_type', False)
        company_id = self.env['res.company']._company_default_get('account.bank.statement').id
        if journal_type:
            journals = self.env['account.journal'].search([('type', '=', journal_type), ('company_id', '=', company_id)])
            if journals:
                return journals[0]
        return self.env['account.journal']

    reference = fields.Char(string='External Reference', states={'open': [('readonly', False)]}, copy=False, readonly=True, track_visibility='onchange', help="Used to hold the reference of the external mean that created this statement (name of imported file, reference of online synchronization...)")
    date = fields.Date(required=True, states={'confirm': [('readonly', True)]}, index=True, copy=False, default=fields.Date.context_today, track_visibility='onchange')
    balance_start = fields.Monetary(string='Starting Balance', states={'confirm': [('readonly', True)]}, default=_default_opening_balance, track_visibility='onchange')
    balance_end_real = fields.Monetary('Ending Balance', states={'confirm': [('readonly', True)]}, track_visibility='onchange')
    state = fields.Selection([('open', 'New'), ('confirm', 'Validated')], string='Status', required=True, readonly=True, copy=False, default='open', track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'confirm': [('readonly', True)]}, default=_default_journal, track_visibility='onchange')
    notes = fields.Char('Notes', track_visibility='onchange')
    default_account_id = fields.Many2one('account.account', 'Default Counterpart Account', track_visibility='onchange')
    default_account_analytic_id = fields.Many2one('account.analytic.account', 'Default Analytic Acc (Dept)', track_visibility='onchange')
    other_note = fields.Char('Other Notes', track_visibility='onchange')

    @api.multi
    def button_cancel_all_reconciliation(self):
        self.ensure_one()
        for line in self.line_ids.filtered(lambda x: x.journal_entry_ids and x.state == 'open' ) :
            info = "Journal entry " +line.journal_entry_ids[0].name+ " Success deleted.." 
            line.button_cancel_reconciliation()
            line._cr.commit()
            print info
        # cari jurnal interco dengan ref yg sama
        if self.name :
            int_exist = self.env['account.move'].sudo().search([('ref','=',self.name)])
            if int_exist :
                for mv in int_exist :
                    mv.button_cancel()
                    mv.unlink()
                    self.other_note = 'Success Unreconciled'
                    self._cr.commit()

    @api.multi
    def button_delete_number_reconciliation(self):
        self.ensure_one()
        for line in self.line_ids.filtered(lambda x: not x.journal_entry_ids and x.state == 'open' ) :
            info = ''
            if line.move_name :
                info = "Journal entry name" +line.move_name+ " Success deleted.." 
            line.write({'move_name' : False})
            print info
        self.other_note = 'Journal entry name success deleted'

    # @api.multi
    # def check_confirm_bank(self):
    #     self.ensure_one()
    #     for x in self :
    #         interco_exist = x.line_ids.filtered(lambda x: x.journal_interco_id and not x.account_interco_id)
    #         if interco_exist :
    #             label = interco_exist[0].name
    #             raise UserError(_('Inter company account statement %s belum diisi ') % (label))
    #     return super(AccountBankStatement, self).check_confirm_bank()

    # @api.multi
    # def button_confirm_bank_partial(self):
    #     self._balance_check()
    #     moves = self.env['account.move']
    #     for st_line in self.line_ids.filtered(lambda x: x.account_id != False and not x.journal_entry_ids):
    #         st_line.fast_counterpart_creation()
    #         moves = (moves | st_line.journal_entry_ids)
    #         self._cr.commit()
    #     if moves:
    #         moves.post()
    #     statement.message_post(body=_('Statement %s confirmed, journal items were created.') % (statement.name,))
    #     statements.link_bank_to_partner()
    #     statements.write({'state': 'confirm', 'date_done': time.strftime("%Y-%m-%d %H:%M:%S")})

AccountBankStatement()


class AccountBankStatementLine(models.Model):
    _name = "account.bank.statement.line"
    _inherit = ['mail.thread','ir.needaction_mixin','account.bank.statement.line']

    @api.model
    def create(self, vals):
        acc= self.env['account.account']
        if 'account_id' in vals :
            account = acc.browse(vals['account_id'])
            move = self.env['account.bank.statement'].browse(vals['statement_id'])
            new_account = acc.sudo().search([('code','=',account.code),('company_id','=',move.company_id.id)])
            if new_account :
                vals['account_id'] = new_account.id
                vals['company_id'] = new_account.company_id.id
        return super(AccountBankStatementLine, self).create(vals)

    @api.onchange('journal_interco_id')
    def onchange_journal_interco_id(self):
        for i in self:
            if i.journal_interco_id:
                journal = self.env["account.journal"].sudo()
                account = self.env["account.account"].sudo()
                i.company_interco_id = i.journal_interco_id.company_id.id
                if i.amount < 0.0 :
                    coa_code = i.journal_interco_id.account_interco_debit_id.code
                    if coa_code :
                        coa = account.search([('code','=',coa_code),('company_id','=',self.env.user.company_id.id)],limit=1)
                        i.account_id = coa.id
                        i.account_interco_id = i.journal_interco_id.default_credit_account_id.id
                elif i.amount > 0.0 :
                    coa_code = i.journal_interco_id.account_interco_credit_id.code
                    if coa_code :
                        coa = account.search([('code','=',coa_code),('company_id','=',self.env.user.company_id.id)],limit=1)
                        i.account_id = coa.id
                        i.account_interco_id = i.journal_interco_id.default_debit_account_id.id
            else :
                i.account_id = False
                i.account_interco_id = False

    @api.onchange('name','partner_id')
    def onchange_auto_save(self):
        #import pdb;pdb.set_trace()
        for i in self:
            if self._origin.id:
                if i.name:
                    sql = "update account_bank_statement_line set name = '%s' where id = %s" % (i.name, self._origin.id)
                    self.env.cr.execute(sql)
                if i.partner_id:
                    sql2 = "update account_bank_statement_line set partner_id = %s where id = %s" % (i.partner_id.id, self._origin.id)
                    self.env.cr.execute(sql2)
                self._cr.commit()

    name = fields.Char(string='Label', required=True, track_visibility='onchange')
    date = fields.Date(required=True, default=lambda self: self._context.get('date', fields.Date.context_today(self)), track_visibility='onchange')
    amount = fields.Monetary(digits=0, currency_field='journal_currency_id', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='onchange')
    note = fields.Text(string='Notes', track_visibility='onchange')
    company_interco_id = fields.Many2one('res.company', 'Inter Company', related="journal_interco_id.company_id", store=True)
    journal_interco_id = fields.Many2one('account.journal', 'Interco Journal')
    account_interco_id = fields.Many2one('account.account', 'Interco Account')
    account_analytic_tag_id = fields.Many2one("account.analytic.tag", string="Analytic Tag (Store)", track_visibility='onchange', related="partner_id.account_analytic_tag_id", store=True)
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Acc (Dept)')
    account_analytic_interco_id = fields.Many2one('account.analytic.account', 'Analytic Acc (Dept Interco)')


    def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
        """

        :param counterpart_aml_dicts:
        :param payment_aml_rec:
        :param new_aml_dicts:
        :return:
        """
        tags = False
        parts = []
        if new_aml_dicts :
            for nad in new_aml_dicts :
                tag = nad.get('analytic_tag_ids', False)
                if tag :
                    tags = [(6, 0, [tag])]
                    nad.update({'analytic_tag_ids':tags})
                part = nad.get('partner_id', False) #0
                if part :
                    # ga bisa insert dg cara update
                    # nad.update({'partner_id':part[0]})
                    label = [nad.get('name')] #1
                    account = [nad.get('account_id')] #2
                    amount = [nad.get('debit')+nad.get('credit')] #3
                    try:
                        parm =  part + label + account + amount
                        parts.append(parm)
                    except:
                        pass

        res = super(AccountBankStatementLine, self).process_reconciliation(counterpart_aml_dicts=counterpart_aml_dicts, payment_aml_rec=payment_aml_rec, new_aml_dicts=new_aml_dicts)
        for x in self :
            account_move_line = self.env["account.move.line"]
            # update account analytic id
            if x.account_analytic_id or parts:
                update_posted = False
                if not res.journal_id.update_posted :
                    res.journal_id.update_posted = True
                    update_posted = True
                for line in res.line_ids.filtered(lambda i: i.company_id.id == x.company_id.id ) :
                    line.update({'analytic_account_id' : x.account_analytic_id.id or False})
                    if parts :
                        res.button_cancel()
                        for par in parts :
                            t_amount = line.debit + line.credit
                            if line.name == par[1] and line.account_id.id == par[2] and t_amount == float(par[3]) :
                                line.update({'partner_id' : par[0]})
                        res.post()
                if update_posted :
                    res.journal_id.update_posted = False
            tag_id = False
            if x.account_analytic_tag_id :
                tag_id = [(6, 0, [x.account_analytic_tag_id.id])]
                move_line_ids = account_move_line.search([('statement_id','=',x.statement_id.id),('name','=',x.name)])
                move_line_ids.write({'analytic_tag_ids'  : tag_id})
            if x.journal_interco_id :
                company_currency = x.journal_interco_id.company_id.currency_id
                statement_currency = x.journal_interco_id.currency_id or company_currency
                st_line_currency =  statement_currency
                amount_currency = False
                st_line_currency_rate = self.currency_id and (self.amount_currency / self.amount) or False
                # We have several use case here to compure the currency and amount currency of counterpart line to balance the move:
                if st_line_currency != company_currency and st_line_currency == statement_currency:
                    # company in currency A, statement in currency B and transaction in currency B
                    # counterpart line must have currency B and correct amount is inverse of already existing lines
                    amount_currency = -sum([x.amount_currency for x in move.line_ids])
                elif st_line_currency != company_currency and statement_currency == company_currency:
                    # company in currency A, statement in currency A and transaction in currency B
                    # counterpart line must have currency B and correct amount is inverse of already existing lines
                    amount_currency = -sum([x.amount_currency for x in move.line_ids])
                elif st_line_currency != company_currency and st_line_currency != statement_currency:
                    # company in currency A, statement in currency B and transaction in currency C
                    # counterpart line must have currency B and use rate between B and C to compute correct amount
                    amount_currency = -sum([x.amount_currency for x in move.line_ids])/st_line_currency_rate
                elif st_line_currency == company_currency and statement_currency != company_currency:
                    # company in currency A, statement in currency B and transaction in currency A
                    # counterpart line must have currency B and amount is computed using the rate between A and B
                    amount_currency = amount/st_line_currency_rate
                account_move = self.env["account.move"]
                
                ref = x.name
                if x.statement_id.name :
                    ref = x.statement_id.name
                lines = []
                account_interco_id = x.account_interco_id.id
                if x.amount < 0 :
                    #import pdb;pdb.set_trace()
                    # jika minus maka interco/bank masuk ke credit
                    datas_line = (0, 0,{'name'          : x.name,
                                    # 'move_id'           : move.id,
                                    'partner_id'        : x.partner_id and x.partner_id.id or False,
                                    'account_id'        : x.journal_interco_id.account_interco_credit_id.id,
                                    'credit'            : x.amount * -1,
                                    'debit'             : 0.0,
                                    'analytic_tag_ids'  : tag_id,
                                    'analytic_account_id' : x.account_analytic_interco_id.id,
                                    'statement_id'      : x.statement_id.id,
                                    'currency_id'       : statement_currency != company_currency and statement_currency.id or (st_line_currency != company_currency and st_line_currency.id or False),
                                    'amount_currency'   : amount_currency,
                                })
                    lines.append(datas_line)
                    if not x.account_interco_id :
                        account_interco_id = x.journal_interco_id.default_debit_account_id.id
                    datas_line2 = (0, 0,{'name'         : x.name,
                                    'partner_id'        : False,
                                    'account_id'        : account_interco_id,
                                    'credit'            : 0.0,
                                    'debit'             : x.amount * -1,
                                    'analytic_tag_ids'  : tag_id,
                                    'analytic_account_id' : x.account_analytic_interco_id.id,
                                    'statement_id'      : x.statement_id.id,
                                    'currency_id'       : statement_currency != company_currency and statement_currency.id or (st_line_currency != company_currency and st_line_currency.id or False),
                                    'amount_currency'   : amount_currency,
                                })
                    lines.append(datas_line2)
                elif x.amount > 0 :
                    # jika plus maka interco masuk ke debit
                    datas_line = (0, 0,{'name'          : ref,
                                    # 'move_id'           : move.id,
                                    'partner_id'        : x.partner_id and x.partner_id.id or False,
                                    'account_id'        : x.journal_interco_id.account_interco_debit_id.id,
                                    'credit'            : 0.0,
                                    'debit'             : x.amount,
                                    'analytic_tag_ids'  : tag_id,
                                    'analytic_account_id' : x.account_analytic_interco_id.id,
                                    'statement_id'      : x.statement_id.id,
                                    'currency_id'       : statement_currency != company_currency and statement_currency.id or (st_line_currency != company_currency and st_line_currency.id or False),
                                    'amount_currency'   : amount_currency,
                                })
                    lines.append(datas_line)
                    if not x.account_interco_id :
                        account_interco_id = x.journal_interco_id.default_credit_account_id.id

                    datas_line2 = (0, 0,{'name'         : ref,
                                    'partner_id'        : False,
                                    'account_id'        : account_interco_id,
                                    'credit'            : x.amount,
                                    'debit'             : 0.0,
                                    'analytic_tag_ids'  : tag_id,
                                    'analytic_account_id' : x.account_analytic_interco_id.id,
                                    'statement_id'      : x.statement_id.id,
                                    'currency_id'       : statement_currency != company_currency and statement_currency.id or (st_line_currency != company_currency and st_line_currency.id or False),
                                    'amount_currency'   : amount_currency,
                                })
                    lines.append(datas_line2)

                if lines :
                    datas = {'ref'              : ref,
                            'journal_id'        : x.journal_interco_id.id,
                            'date'              : x.date,
                            'company_id'        : x.journal_interco_id.company_id.id,
                            'statement_line_id' : x.id,
                            'line_ids'          : lines}

                    journal_interco = account_move.create(datas)
                    info = "Journal Inter Company "+ str(x.journal_interco_id.company_id.name)+" Created.."
                    print info
                    # journal_interco.post()
                    # extra_info = "Journal Inter Company "+ str(x.company_interco_id.name) +" Posted"
                    # print extra_info
        return res


    @api.multi
    def process_reconciliations(self, data):
        """ Handles data sent from the bank statement reconciliation widget (and can otherwise serve as an old-API bridge)

            :param list of dicts data: must contains the keys 'counterpart_aml_dicts', 'payment_aml_ids' and 'new_aml_dicts',
                whose value is the same as described in process_reconciliation except that ids are used instead of recordsets.
        """
        AccountMoveLine = self.env['account.move.line']
        for st_line, datum in zip(self, data):
            payment_aml_rec = AccountMoveLine.browse(datum.get('payment_aml_ids', []))
            for aml_dict in datum.get('counterpart_aml_dicts', []):
                # aml_dict['counterpart_aml_id']  sering error
                if aml_dict.get('counterpart_aml_id',False) :
                    aml_dict['move_line'] = AccountMoveLine.browse(aml_dict['counterpart_aml_id'])
                    del aml_dict['counterpart_aml_id']
            st_line.process_reconciliation(datum.get('counterpart_aml_dicts', []), payment_aml_rec, datum.get('new_aml_dicts', []))


    def fast_counterpart_creation(self):
        cr = self.env.cr
        if not self.journal_interco_id :
            res = self.super_fast_counterpart_creation()
            _logger.info( "Bank statement line Non Interco %s (%s) ==========> entries created.." % (self.name, self.statement_id.name))
        else :
            res = super(AccountBankStatementLine, self).fast_counterpart_creation()
            _logger.info( "Bank statement line Interco %s (%s) ==========> entries created.." % (self.name, self.statement_id.name))
        self._cr.commit()
        notbypass = self.statement_id.line_ids.filtered(lambda x : not x.journal_entry_ids)
        if notbypass :
            return res
        else :
            # sql_statement = "UPDATE account_bank_statement SET state='confirm' and date_done=%s WHERE id=%s "
            # cr.execute(sql_statement, (time.strftime("%Y-%m-%d %H:%M:%S"), self.statement_id.id))
            self.statement_id.write({'state': 'confirm', 'date_done': time.strftime("%Y-%m-%d %H:%M:%S")})
            self._cr.commit()
            _logger.info("Bank statement %s  ====================> success validated.." % (self.statement_id.name))



    def super_fast_counterpart_creation(self):
        cr = self.env.cr
        company_id = self.statement_id.company_id.id
        journal_id = self.statement_id.journal_id.id
        date = self.date
        ref = self.statement_id.name
        amount = self.amount
        #try:
        # Account tag
        account_analytic_tag_id = False
        if self.account_analytic_tag_id:
            account_analytic_tag_id = self.account_analytic_tag_id.id

        move_id = self.create_account_move_manual(journal_id, company_id, date, ref, amount)
        if amount > 0.0 :
            # CoA
            bank_account_id = self.statement_id.journal_id.default_debit_account_id.id
            credit_id = self.account_id.id
            move_line_id1 = self.create_account_move_line_manual(move_id.id, self.name,
                                                                 journal_id, bank_account_id, company_id,
                                                                 date, date, amount, 0.0, ref, account_analytic_tag_id)
            move_line_id2 = self.create_account_move_line_manual(move_id.id, self.name,
                                                                 journal_id, credit_id, company_id,
                                                                 date, date, 0.0, amount, ref, account_analytic_tag_id)
        else :
            debit_id = self.account_id.id
            bank_account_id = self.statement_id.journal_id.default_credit_account_id.id
            move_line_id1 = self.create_account_move_line_manual(move_id.id, self.name,
                                                                 journal_id, bank_account_id, company_id,
                                                                 date, date, 0.0, amount, ref, account_analytic_tag_id)
            move_line_id2 = self.create_account_move_line_manual(move_id.id, self.name,
                                                                 journal_id, debit_id,company_id,
                                                                date, date, amount, 0.0, ref, account_analytic_tag_id)
        # partner
        partner_id = False
        if self.partner_id :
            partner_id = self.partner_id.id
        if partner_id:
            sql_partner = "UPDATE account_move_line set partner_id=%s where id=%s or id=%s"
            cr.execute(sql_partner, (partner_id, move_line_id1,move_line_id2))
        # Account Analytic
        account_analytic_id = False
        if self.account_analytic_id :
            account_analytic_id = self.account_analytic_id.id
            if account_analytic_id:
                sql_analytic = "UPDATE account_move_line SET analytic_account_id=%s WHERE id=%s or id=%s"
                cr.execute(sql_analytic, (account_analytic_id, move_line_id1,move_line_id2))
        move_id.post()
        _logger.info("Create Journal entries %s ========> (%s) successed..." % (self.name,self.statement_id.name))
        self._cr.commit()
        # except Exception:
        #     move_id.unlink()
        #     _logger.info("Create journal entries %s ========> (%s) failed..." % (self.name,self.statement_id.name))

    def create_account_move_manual(self, journal_id, company_id, date, ref, amount):
        cr = self.env.cr
        create_date = time.strftime("%Y-%m-%d %H:%M:%S")
        write_date = time.strftime("%Y-%m-%d %H:%M:%S")

        sql = """INSERT INTO "account_move" (
        "create_uid", "write_uid", "create_date", "write_date",
        "name",
        "company_id", 
        "journal_id",
        "date", 
        "ref", 
        "amount", 
        "statement_line_id",
        "state"
        ) VALUES     
        """
        sql = sql + str((
            self._uid, self._uid, create_date, write_date,
            '/',
            company_id,
            journal_id,
            date,
            str(ref),
            abs(amount),
            self.id,
            'draft'
        ))

        sql = sql + " RETURNING id"
        cr.execute(sql)
        move_id = cr.fetchone()[0]
        return self.env['account.move'].browse(move_id)


    def create_account_move_line_manual(self, move_id, name, journal_id,account_id, company_id,
                                        date, due_date, debit, credit, ref, account_analytic_tag_id):
        cr = self.env.cr
        create_date = time.strftime("%Y-%m-%d %H:%M:%S")
        write_date = time.strftime("%Y-%m-%d %H:%M:%S")
        debit = abs(debit)
        credit = abs(credit)
        reconciled = False
        currency_id = 13
        balance = debit-credit
        amount_residual = balance
        amount_currency = credit
        quantity = 1

        sql = """INSERT INTO "account_move_line" (
        "name", 
        "reconciled", 
        "currency_id", 
        "credit", 
        "debit", 
        "amount_currency", 
        "move_id", 
        "account_id",
        "date_maturity",
        "create_uid", "write_uid", "create_date", "write_date",
        "quantity",
        "company_id",
        "journal_id",
        "date",
        "balance",
        "amount_residual",
        "ref",
        "statement_id"
        ) VALUES     
        """
        sql = sql + str((
            str(name),
            reconciled,
            currency_id,
            credit,
            debit,
            amount_currency,
            move_id,
            account_id,
            due_date,
            self._uid, self._uid, create_date, write_date, quantity,
            company_id,
            journal_id,
            date,
            balance,
            amount_residual,
            str(ref),
            self.statement_id.id
        ))

        sql = sql + " RETURNING id"
        cr.execute(sql)
        move_line_id = cr.fetchone()[0]

        if account_analytic_tag_id:
            sql = "INSERT INTO account_analytic_tag_account_move_line_rel (account_move_line_id,account_analytic_tag_id) VALUES (%s,%s)"
            cr.execute(sql, (move_line_id, account_analytic_tag_id))

        return move_line_id


AccountBankStatementLine()


class VitBankStatementImport(models.Model):
    _inherit = 'vit.bank.statement.import'

    @api.multi
    def action_process(self):
        res = super(VitBankStatementImport, self).action_process()
        if self.notes and self.bank_statement_id:
            self.bank_statement_id.notes = self.notes
        return res

VitBankStatementImport()

class BankStatementWizard(models.TransientModel):
    _name = "bank.statement.wizard"

    @api.multi
    def action_insert_counterpart_account(self):
        self.ensure_one()
        for i in self.statement_id:
            for line in i.line_ids :
                if not line.account_id and not line.journal_entry_ids and self.default_account_id :
                    sql = "update account_bank_statement_line set account_id = %s where id = %s" % (self.default_account_id.id, line.id )
                    self.env.cr.execute(sql)
                if not line.account_analytic_id  and not line.journal_entry_ids and self.default_account_analytic_id :
                    sql2 = "update account_bank_statement_line set account_analytic_id = %s where id = %s" % (self.default_account_analytic_id.id, line.id )
                    self.env.cr.execute(sql2)
                self.env.cr.commit()
            if self.default_account_id :
                sql3 = "update account_bank_statement set default_account_id = %s where id = %s" % (self.default_account_id.id, self.statement_id.id )
                self.env.cr.execute(sql3)
            if self.default_account_analytic_id :
                sql4 = "update account_bank_statement set default_account_analytic_id = %s where id = %s" % (self.default_account_analytic_id.id, self.statement_id.id )
                self.env.cr.execute(sql4)
            if self.partner_id :
                sql5 = "update account_bank_statement_line set partner_id = %s where statement_id = %s and partner_id is null" % (self.partner_id.id, self.statement_id.id )
                self.env.cr.execute(sql5)
            self.env.cr.commit()
            return {'type': 'ir.actions.client','tag': 'reload'}

    default_account_id = fields.Many2one('account.account', 'Counterpart Account')
    default_account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Acc (Dept)')
    statement_id = fields.Many2one('account.bank.statement','Statement')
    company_id = fields.Many2one('res.company','Company')
    partner_id = fields.Many2one('res.partner','Partner')

    @api.model
    def default_get(self, fields):
        res = super(BankStatementWizard, self).default_get(fields)
        if 'statement_id' in fields and not res.get('statement_id') and self._context.get('active_model') == 'account.bank.statement' and self._context.get('active_id'):
            res['statement_id'] = self._context['active_id']
        if 'company_id' in fields and not res.get('company_id') and res.get('statement_id'):
            company_id = self.env['account.bank.statement'].browse(res.get('statement_id')).company_id.id
            res['company_id'] = company_id
        return res

BankStatementWizard()
