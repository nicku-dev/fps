from odoo import fields, api, SUPERUSER_ID,  models, _
from odoo.exceptions import Warning, UserError, ValidationError, AccessError
from odoo.addons import decimal_precision as dp

class Uudp(models.Model):
    _inherit = 'uudp'

    @api.depends('ajuan_id.company_id','company_id','invoice_line.invoice_id.company_id')
    @api.multi
    def _is_intercompany(self):
        for me_id in self :
            if me_id.ajuan_id :
                me_id.is_intercompany = any(me_id.ajuan_id.company_id != inv.invoice_id.company_id for inv in me_id.invoice_line)
            else :
                me_id.is_intercompany = False


    @api.depends('invoice_line.alokasi')
    @api.multi
    def _get_tot_alokasi(self):
        for me_id in self :
            me_id.tot_alokasi = sum(inv.alokasi for inv in me_id.invoice_line)

    purchase_line = fields.One2many(comodel_name='uudp.purchase.order', inverse_name='uudp_id', string='Purchase Line', copy=True)
    invoice_line = fields.One2many(comodel_name='uudp.account.invoice', inverse_name='uudp_id', string='Invoice Line', copy=True)
    advance_purchase_id = fields.Many2one(comodel_name='account.account', string='Advance Purchase', ondelete='restrict')
    is_po = fields.Boolean('Purchase Order')
    is_intercompany = fields.Boolean(string='Is Intercompany', compute='_is_intercompany')
    tot_alokasi = fields.Float(string='Total Alokasi', compute='_get_tot_alokasi')

    @api.onchange('company_id')
    def company_change(self):
        if self.company_id.id != self.ajuan_id.company_id.id :
            self.purchase_line = False

    @api.multi
    def update_purchase_invoice(self):
        for me_id in self :
            for purchase in me_id.purchase_line :
                if me_id.type == 'penyelesaian' :
                    purchase.purchase_id.write({'penyelesaian_id':me_id.id})
                elif me_id.type == 'reimberse' :
                    purchase.purchase_id.write({'reimburse_id':me_id.id})
            for invoice in me_id.invoice_line :
                if me_id.type == 'penyelesaian' :
                    invoice.invoice_id.write({'penyelesaian_id':me_id.id})
                elif me_id.type == 'reimberse' :
                    invoice.invoice_id.write({'reimburse_id':me_id.id})

    @api.multi
    def create_payment(self):
        for me_id in self :
            if me_id.purchase_line :
                # delete dulu jurnal lama supaya ga double
                aju = me_id.ajuan_id.name
                if aju :
                    entries = self.env['account.move'].sudo().search([('ref','=',me_id.name+ ' - ' + aju)])
                    if entries :
                        for ent in entries :
                            try :
                                cenceling_journal = False
                                if ent.journal_id.update_posted :
                                    ent.write({'update_posted' : False})
                                    cenceling_journal = True
                                entries.sudo(SUPERUSER_ID).button_cancel()
                                if cenceling_journal :
                                    ent.write({'update_posted' : True})
                                ent.sudo(SUPERUSER_ID).unlink()
                            except :
                                pass
                for purchase in me_id.purchase_line :
                    if purchase.down_payment <= 0.0:
                        continue
                    if me_id.type == 'penyelesaian' :
                        if not me_id.ajuan_id.pencairan_id :
                            raise Warning("Ajuan %s belum dicairkan."%me_id.ajuan_id.name)
                        payment_methods = me_id.ajuan_id.pencairan_id.journal_id.outbound_payment_method_ids
                        journal_id = me_id.ajuan_id.pencairan_id.journal_id.id
                        #cari jurnal uudp
                        uudp_journal = self.env['account.journal'].search([('name','=','UUDP'),('company_id','=',me_id.company_id.id)],limit=1) 
                        if uudp_journal :
                            payment_methods = uudp_journal.outbound_payment_method_ids
                            journal_id = uudp_journal.id
                        name = me_id.ajuan_id.name
                        date =me_id.date
                        com = me_id.name + ' - ' + name +' - ' + purchase.purchase_id.name
                    else :
                        payment_methods = me_id.pencairan_id.journal_id.outbound_payment_method_ids
                        journal_id = me_id.pencairan_id.journal_id.id
                        name = me_id.pencairan_id.name
                        if not name :
                            raise Warning("Tidak ada id pencairan di nomor dokumen ini (%s)"%me_id.name)
                        date = me_id.pencairan_id.tgl_pencairan
                        com = me_id.name + ' - ' + name +' - ' + purchase.purchase_id.name
                    # delete dulu jurnal lama supaya ga double
                    entries = self.env['account.move'].sudo().search([('ref','=',com)])
                    if entries :
                        for ent in entries :
                            try :
                                cenceling_journal = False
                                if ent.journal_id.update_posted :
                                    ent.write({'update_posted' : False})
                                    cenceling_journal = True
                                entries.sudo(SUPERUSER_ID).button_cancel()
                                if cenceling_journal :
                                    ent.write({'update_posted' : True})
                                ent.sudo(SUPERUSER_ID).unlink()
                            except :
                                pass

                    payment_method_id = payment_methods and payment_methods[0] or False
                    # cek jika sudah ada memo yg sama maka di by pass
                    payment_exist = self.env['account.payment'].sudo().search([('communication','=',com)])
                    if not payment_exist :
                        # jika advance purchase tidak bertype payable maka create payment aga bisa recon di inv
                        if me_id.advance_purchase_id.user_type_id.type != 'payable' :

                            payment_id = self.env['account.payment'].create({
                                'payment_type': 'outbound',
                                'partner_type': 'supplier',
                                'partner_id': purchase.purchase_id.partner_id.id,
                                'journal_id': journal_id,
                                'payment_method_id': payment_method_id.id,
                                'payment_date': date,
                                'communication': com,
                                'amount': purchase.down_payment,
                                'company_id': me_id.company_id.id,
                            })
                            purchase.write({'payment_id':payment_id.id})
                            #raise Warning("journal (%s) %s"%(journal_id,payment_method_id.name))
                            if not payment_id.destination_account_id :
                                raise Warning("Default AR/AP partner %s belum di set (Company %s)"%(purchase.purchase_id.partner_id.name,me_id.company_id.name))  
                            payment_id.post()

    @api.multi
    def create_payment_invoice(self):
        for me_id in self :
            if me_id.invoice_line :
                # delete dulu jurnal lama supaya ga double
                if me_id.ajuan_id.name :
                    entries = self.env['account.move'].sudo().search([('ref','=',me_id.name+ ' - ' +me_id.ajuan_id.name)])
                    if entries :
                        for ent in entries :
                            try :
                                cenceling_journal = False
                                if ent.journal_id.update_posted :
                                    ent.write({'update_posted' : False})
                                    cenceling_journal = True
                                entries.sudo(SUPERUSER_ID).button_cancel()
                                if cenceling_journal :
                                    ent.write({'update_posted' : True})
                                ent.sudo(SUPERUSER_ID).unlink()
                            except :
                                pass
                for inv in me_id.invoice_line.filtered(lambda i:i.state == 'open') :
                    if inv.alokasi <= 0.0:
                        continue
                    if me_id.type == 'penyelesaian' :
                        if not me_id.ajuan_id.pencairan_id :
                            raise Warning("Ajuan %s belum dicairkan."%me_id.ajuan_id.name)
                        payment_methods = me_id.ajuan_id.pencairan_id.journal_id.outbound_payment_method_ids
                        journal_id = me_id.ajuan_id.pencairan_id.journal_id.id
                        name = me_id.ajuan_id.name
                        date = me_id.date
                        com = me_id.name + ' - ' + name +' - ' + inv.invoice_id.number
                    else :
                        payment_methods = me_id.pencairan_id.journal_id.outbound_payment_method_ids
                        journal_id = me_id.pencairan_id.journal_id.id
                        name = me_id.pencairan_id.name
                        if not name :
                            raise Warning("Pencairan %s not found "%me_id.name)
                        if not me_id.name :
                            raise Warning("Ajuan %s not found "%me_id.name)
                        if not inv.invoice_id :
                            raise Warning("Invoice %s not found "%me_id.name)
                        date = me_id.pencairan_id.tgl_pencairan
                        com = me_id.name + ' - ' + name +' - ' + inv.invoice_id.number

                    entries = self.env['account.move'].sudo().search([('ref','=',com)])
                    if entries :
                        for ent in entries :
                            try :
                                cenceling_journal = False
                                if ent.journal_id.update_posted :
                                    ent.write({'update_posted' : False})
                                    cenceling_journal = True
                                entries.sudo(SUPERUSER_ID).button_cancel()
                                if cenceling_journal :
                                    ent.write({'update_posted' : True})
                                ent.sudo(SUPERUSER_ID).unlink()
                            except :
                                pass

                    payment_method_id = payment_methods and payment_methods[0] or False
                    # cek jika sudah ada memo yg sama maka di by pass
                    payment_exist = self.env['account.payment'].sudo().search([('communication','=',com)])
                    if not payment_exist :
                        # jika advance purchase tidak bertype payable maka create payment aga bisa recon di inv
                        if me_id.advance_purchase_id.user_type_id.type != 'payable' :
                            payment_id = self.env['account.payment'].create({
                                'payment_type': 'outbound',
                                'partner_type': 'supplier',
                                'partner_id': inv.invoice_id.partner_id.id,
                                'journal_id': journal_id,
                                'payment_method_id': payment_method_id.id,
                                'payment_date': date,
                                'communication': com,
                                'amount': inv.alokasi,
                                'company_id': me_id.company_id.id,
                                'invoice_ids': [(6, 0, [inv.invoice_id.id])],
                            })
                            payment_id.post()

    @api.multi
    def get_tot_detail(self):
        self.ensure_one()
        tot_detail = 0
        for detail in self.uudp_ids :
            if detail.sub_total > 0 :
                tot_detail += detail.sub_total
        return tot_detail

    @api.multi
    def validity_check(self):
        for me_id in self :
            if not me_id.invoice_line and not me_id.purchase_line :
                raise ValidationError("Detail PO atau Vendor Bills harus diisi.")
            if me_id.invoice_line and not me_id.advance_purchase_id :
                raise ValidationError("Silahkan input advance purchase.")
            tot_purchase = 0
            for purchase in me_id.purchase_line :
                if purchase.purchase_id.penyelesaian_id :
                    if me_id.type == 'penyelesaian' and purchase.purchase_id.penyelesaian_id.id != me_id.id  :
                        raise ValidationError("PO %s sudah diselesaikan di %s."%(purchase.purchase_id.name,purchase.purchase_id.penyelesaian_id.name))
                if purchase.purchase_id.reimburse_id :
                    if me_id.type == 'reimberse' and purchase.purchase_id.reimburse_id.id != me_id.id :
                        raise ValidationError("PO %s sudah direimburse di %s."%(purchase.purchase_id.name,purchase.purchase_id.reimburse_id.name))
                if purchase.purchase_id.invoice_status == 'invoiced' :
                    raise ValidationError("PO %s sudah diinvoice." % (purchase.purchase_id.name))
                tot_purchase += purchase.down_payment
            for invoice in me_id.invoice_line :
                if not invoice.alokasi :
                    raise Warning("Alokasi tidak boleh nol.")
                if invoice.invoice_id.penyelesaian_id :
                    if me_id.type == 'penyelesaian' and invoice.invoice_id.penyelesaian_id.id != me_id.id  :
                        raise ValidationError("Vendor Bills %s sudah diselesaikan di %s."%(invoice.invoice_id.number,invoice.invoice_id.penyelesaian_id.name))
                if invoice.invoice_id.reimburse_id :
                    if me_id.type == 'reimberse' and invoice.invoice_id.reimburse_id.id != me_id.id  :
                        raise ValidationError("Vendor Bills %s sudah direimburse di %s."%(invoice.invoice_id.name,invoice.invoice_id.reimburse_id.name))
                if not invoice.company_id.intercompany_payable_id or not invoice.company_id.intercompany_receivable_id :
                    raise Warning("Silahkan lengkapi intercompany payable dan receivable company %"%(invoice_id.company_id.name))
            tot_penyelesaian = self.get_tot_detail()
            dp = (me_id.tot_alokasi + tot_purchase)
            if round(tot_penyelesaian,2) < round(dp,2):
                #raise Warning("Total alokasi invoice dan atau down payment purchase harus sama dengan total penyelesaian/reimburse.")
                raise UserError(_(
                    'Total alokasi invoice dan atau down payment purchase (%s) harus sama dengan total penyelesaian/reimburse (%s) !') % (
                                dp,
                                tot_penyelesaian))
            # if me_id.type == 'penyelesaian' :
            #     tot_dp = sum(me_id.purchase_line.mapped('down_payment'))
            #     tot_inv = sum(me_id.invoice_line.mapped('amount_total'))
            #     tot_penyelesaian = tot_dp + tot_inv
            #     if tot_penyelesaian > me_id.total_ajuan_penyelesaian :
            #         raise ValidationError("Total PO dan Bills tidak boleh melebihi total pencairan.")

    @api.multi
    def create_account_move(self):
        for me_id in self :
            if not me_id.is_intercompany :
                for invoice in me_id.invoice_line :
                    account_move_line = []
                    to_reconcile = self.env['account.move.line']
                    for move_line in invoice.invoice_id.move_id.line_ids :
                        if move_line.account_id.internal_type == 'payable' and not move_line.reconciled :
                            to_reconcile += move_line
                            account_move_line.append((0, 0, {
                                'account_id' : move_line.account_id.id,
                                'partner_id' : move_line.partner_id.id,
                                'analytic_tag_ids' : [(6, 0, [tag.id for tag in move_line.analytic_tag_ids])] if move_line.analytic_tag_ids else False,
                                'name' : me_id.notes,
                                'analytic_account_id' : me_id.department_id.analytic_account_id.id,
                                'debit' : invoice.alokasi,
                                'credit': 0,
                                'date_maturity' : me_id.date,
                                'company_id' : me_id.company_id.id,
                            }))
                    partner = invoice.partner_id.id
                    # if me_id.type == 'penyelesaian' :
                    #     partner = me_id.ajuan_id.responsible_id.partner_id.id
                    # elif me_id.type == 'reimberse':
                    #     partner = me_id.responsible_id.partner_id.id
                    account_move_line.append((0, 0, {
                        'account_id' : me_id.coa_kredit.id,
                        'partner_id' : partner,
                        'analytic_tag_ids' : False,
                        'name' : me_id.notes,
                        'analytic_account_id' : me_id.department_id.analytic_account_id.id,
                        'debit' : 0,
                        'credit': invoice.alokasi,
                        'date_maturity' : me_id.date,
                        'company_id' : me_id.company_id.id,
                    }))
                    if me_id.type == 'penyelesaian':
                        journal_id = me_id.ajuan_id.pencairan_id.journal_id.id
                    else:
                        journal_id = me_id.pencairan_id.journal_id.id
                    move_id = self.env['account.move'].create({
                        "partner_id": partner,
                        "journal_id": journal_id,
                        "ref": me_id.pencairan_id.name + ' - ' + me_id.name,
                        "date": me_id.date,
                        "narration": me_id.notes,
                        "company_id": me_id.company_id.id,
                        "line_ids": account_move_line,
                    })
                    move_id.post()
                    if to_reconcile :
                        to_reconcile.reconcile()
            else :
                tot_penyelesaian = self.get_tot_detail()
                company_ids = me_id.invoice_line.mapped('company_id')
                parent_company_id = me_id.ajuan_id.company_id
                account_move_line_parent = []
                adv_purchase_parent_amount = 0
                tot_adv_purchase = 0
                to_reconcile_parent = self.env['account.move.line']
                journal_parent_id = self.env['account.journal'].search([
                    ('type','=','general'),
                    ('company_id','=',parent_company_id.id),
                    ('name','ilike','Miscellaneous%'),
                ], limit=1)
                if not journal_parent_id :
                    raise Warning("Tidak ditemukan journal miscellaneous company %s"%parent_company_id.name)
                for company_id in company_ids :
                    inv_ids = me_id.invoice_line.filtered(lambda inv: inv.invoice_id.company_id.id == company_id.id)
                    #jika ada kemungkinan penyelesaian intercompany sekaligus penyelesaian invoicenya sendiri
                    if company_id == parent_company_id :
                        for inv in inv_ids :
                            for move_line in inv.invoice_id.move_id.line_ids :
                                if move_line.account_id.internal_type == 'payable' and not move_line.reconciled :
                                    to_reconcile_parent += move_line
                                    account_move_line_parent.append((0, 0, {
                                        'account_id' : move_line.account_id.id,
                                        'partner_id' : move_line.partner_id.id,
                                        'analytic_tag_ids' : [(6, 0, [tag.id for tag in move_line.analytic_tag_ids])] if move_line.analytic_tag_ids else False,
                                        'name' : inv.invoice_id.number,
                                        'analytic_account_id' : me_id.department_id.analytic_account_id.id,
                                        'debit' : inv.alokasi,
                                        'credit': 0,
                                        'date_maturity' : me_id.date,
                                    }))
                                    tot_adv_purchase += inv.alokasi
                        partner = False
                        if me_id.type == 'penyelesaian' :
                            partner = me_id.ajuan_id.responsible_id.partner_id.id
                        elif me_id.type == 'reimberse':
                            partner = me_id.responsible_id.partner_id.id
                        account_move_line_parent.append((0, 0, {
                            'account_id' : me_id.advance_purchase_id.id,
                            'partner_id' : partner,
                            'analytic_tag_ids' : False,
                            'name' : me_id.notes,
                            'analytic_account_id' : me_id.department_id.analytic_account_id.id,
                            'debit' : 0,
                            'credit': tot_adv_purchase,
                            'date_maturity' : me_id.date,
                        }))
                    else :
                        journal_id = self.env['account.journal'].search([
                            ('type','=','general'),
                            ('company_id','=',company_id.id),
                            ('name','ilike','Miscellaneous%'),
                        ], limit=1)
                        if not journal_id :
                            raise Warning("Tidak ditemukan journal miscellaneous company %s"%company_id.name)
                        tot_amount = 0
                        to_reconcile = self.env['account.move.line']
                        account_move_line = []
                        advance_purchase_id = self.env['account.account'].search([
                            ('code','=',me_id.advance_purchase_id.code),
                            ('company_id','=',company_id.id),
                        ], limit=1)
                        if not advance_purchase_id :
                            raise Warning("Tidak ditemukan account advance purchase company %s"%(company_id.name))
                        for inv in inv_ids :
                            tot_amount += inv.alokasi
                            for move_line in inv.invoice_id.move_id.line_ids :
                                if move_line.account_id.internal_type == 'payable' and not move_line.reconciled :
                                    to_reconcile += move_line
                                    account_move_line.append((0, 0, {
                                        'account_id' : advance_purchase_id.id,
                                        'partner_id' : False,
                                        'analytic_tag_ids' : False,
                                        'name' : 'Advance purchase %s'%(me_id.name),
                                        'analytic_account_id' : False,
                                        'debit' : 0,
                                        'credit': inv.alokasi,
                                        'date_maturity' : me_id.date,
                                    }))
                                    account_move_line.append((0, 0, {
                                        'account_id' : move_line.account_id.id,
                                        'partner_id' : move_line.partner_id.id,
                                        'analytic_tag_ids' : False,
                                        'name' : 'Hutang supplier %s'%(move_line.invoice_id.number or False),
                                        'analytic_account_id' : False,
                                        'debit' : inv.alokasi,
                                        'credit': 0,
                                        'date_maturity' : me_id.date,
                                    }))
                        
                        account_move_line.append((0, 0, {
                            'account_id' : advance_purchase_id.id,
                            'partner_id' : False,
                            'analytic_tag_ids' : False,
                            'name' : 'Advance purchase %s'%(me_id.name),
                            'analytic_account_id' : False,
                            'debit' : tot_amount,
                            'credit': 0,
                            'date_maturity' : me_id.date,
                        }))
                        account_move_line.append((0, 0, {
                            'account_id' : company_id.intercompany_payable_id.id,
                            'partner_id' : False,
                            'analytic_tag_ids' : False,
                            'name' : 'Hutang intercompany %s'%(me_id.name),
                            'analytic_account_id' : False,
                            'debit' : 0,
                            'credit': tot_amount,
                            'date_maturity' : me_id.date,
                        }))
                        move_id = self.env['account.move'].create({
                            "partner_id": False,
                            "journal_id": journal_id.id,
                            "ref": me_id.name,
                            "date": me_id.date,
                            "narration": me_id.notes,
                            "line_ids": account_move_line,
                        })
                        move_id.post()
                        to_reconcile += move_id.line_ids.filtered(lambda line: line.account_id.internal_type == 'payable' and line.debit > 0)
                        if to_reconcile :
                            to_reconcile.reconcile()

                account_move_line_parent.append((0, 0, {
                    'account_id' : me_id.ajuan_id.company_id.intercompany_receivable_id.id,
                    'partner_id' : False,
                    'analytic_tag_ids' : False,
                    'name' : 'Piutang interco %s'%(me_id.name),
                    'analytic_account_id' : False,
                    'debit' : tot_penyelesaian - tot_adv_purchase,
                    'credit': 0,
                    'date_maturity' : me_id.date,
                }))
                account_move_line_parent.append((0, 0, {
                    'account_id' : me_id.ajuan_id.coa_debit.id,
                    'partner_id' : False,
                    'analytic_tag_ids' : False,
                    'name' : 'UUDP %s'%(me_id.name),
                    'analytic_account_id' : False,
                    'debit' : 0,
                    'credit': tot_penyelesaian - tot_adv_purchase,
                    'date_maturity' : me_id.date,
                }))
                move_id = self.env['account.move'].create({
                    "partner_id": False,
                    "journal_id": journal_parent_id.id,
                    "ref": me_id.name,
                    "date": me_id.date,
                    "narration": me_id.notes,
                    "company_id": me_id.ajuan_id.company_id.id,
                    "line_ids": account_move_line_parent,
                })
                move_id.post()
                to_reconcile_parent += move_id.line_ids.filtered(lambda line: line.account_id.internal_type == 'payable')
                if to_reconcile_parent :
                    to_reconcile_parent.reconcile()

    @api.multi
    def button_confirm(self):
        for me_id in self :
            if me_id.is_po :
                me_id.validity_check()
        return super(Uudp, self).button_confirm()

    @api.multi
    def button_confirm_finance(self):
        for me_id in self :
            if me_id.is_po :
                me_id.validity_check()
        return super(Uudp, self).button_confirm_finance()

    @api.multi
    def button_done_finance(self):
        for me_id in self :
            if me_id.is_po :
                if me_id.purchase_line or me_id.invoice_line:
                    me_id.validity_check()
                    ########### pernah dikomen dulu ################
                    me_id.update_purchase_invoice()
                    me_id.create_payment()
                    me_id.create_payment_invoice()
        return super(Uudp, self).button_done_finance()

    @api.multi
    def button_validate(self):
        for me_id in self :
            if me_id.is_po :
                if me_id.purchase_line or me_id.invoice_line:
                    if me_id.pencairan_id and me_id.pencairan_id.state != 'done' :
                        raise Warning("Pencairan %s belum done !"%me_id.pencairan_id.name)
                    me_id.validity_check()
                    me_id.update_purchase_invoice()
                    me_id.create_payment()
                    me_id.create_payment_invoice()
        return super(Uudp, self).button_validate()

    @api.onchange('is_po')
    def po_change(self):
        if not self.is_po :
            self.purchase_line = False
            self.invoice_line = False
            self.advance_purchase_id = False
        if self.is_po and not self.advance_purchase_id :
            advance_purchase_id = self.env['account.account'].search([
                ('company_id','=',self.company_id.id),
                ('name','=ilike','advanced purchase')
            ], limit=1)
            self.advance_purchase_id = advance_purchase_id and advance_purchase_id.id or False

class UudpPurchaseOrder(models.Model):
    _name = "uudp.purchase.order"
    _description = "UUDP Purchase Order"

    uudp_id = fields.Many2one(comodel_name='uudp', string='UUDP', ondelete='cascade', copy=False)
    purchase_id = fields.Many2one(comodel_name='purchase.order', string='Purchase', required=True)
    partner_id = fields.Many2one(related='purchase_id.partner_id', string='Supplier')
    company_id = fields.Many2one(related='purchase_id.company_id', string='Company')
    currency_id = fields.Many2one(related='purchase_id.currency_id', string='Currency')
    state = fields.Selection(related='purchase_id.state', string='State')
    amount_total = fields.Monetary(related='purchase_id.amount_total', string='Amount', digits=dp.get_precision('Product Price'))
    down_payment = fields.Float(string='DP', digits=dp.get_precision('Product Unit of Measure'), default=0, required=True)
    payment_id = fields.Many2one(comodel_name='account.payment', string='Payment', ondelete='restrict')

    @api.onchange('purchase_id')
    def purchase_change(self):
        if self.purchase_id :
            self.down_payment = self.purchase_id.amount_total
        else :
            self.down_payment = False

class UudpAccountInvoice(models.Model):
    _name = "uudp.account.invoice"
    _description = "UUDP Supplier Invoice"

    uudp_id = fields.Many2one(comodel_name='uudp', string='UUDP', ondelete='cascade', copy=False)
    invoice_id = fields.Many2one(comodel_name='account.invoice', string='Invoice', required=True)
    partner_id = fields.Many2one(related='invoice_id.partner_id', string='Supplier')
    company_id = fields.Many2one(related='invoice_id.company_id', string='Company')
    currency_id = fields.Many2one(related='invoice_id.currency_id', string='Currency')
    state = fields.Selection(related='invoice_id.state', string='State')
    amount_total = fields.Monetary(related='invoice_id.residual', string='Amount', digits=dp.get_precision('Product Price'), default=0)
    alokasi = fields.Float(string='Alokasi', digits=dp.get_precision('Product Price'), default=0, required=True)

class UudpPencairan(models.Model):
    _inherit = 'uudp.pencairan'

    @api.multi
    def button_done_once(self):
        for me_id in self :
            for uudp in me_id.uudp_ids :
                if uudp.is_po :
                    uudp.button_done_finance()
        return super(UudpPencairan, self).button_done_once()
