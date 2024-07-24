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


class pencairanWizard(models.TransientModel):
    _inherit = 'pencairan.wizard'

    @api.model
    def _get_default_journal_id(self):
        if self._context.get('active_id'):
            uudp_obj = self.env['uudp.pencairan']
            uudp = uudp_obj.browse(self._context.get('active_id'))
            return uudp.journal_id.id

    @api.model
    def _get_default_uudp_details(self):
        if self._context.get('active_id'):
            uudp_obj = self.env['uudp.pencairan']
            uudp = uudp_obj.browse(self._context.get('active_id'))
            details_ids = []
            for uu in uudp.ajuan_id.uudp_ids :
                details_ids.append((0, 0, {'product_id': uu.product_id.id , 
                                            'partner_id': uu.partner_id.id,
                                            'store_id' : uu.store_id.id,
                                            'description' : uu.description,
                                            'qty' : uu.qty,
                                            'uom' : uu.uom,
                                            'unit_price' : uu.unit_price,
                                            'sub_total' : uu.sub_total,
                                            'state' : uu.state,
                                            'coa_debit' :uu.coa_debit }))
            return details_ids


    @api.model
    def _get_sisa_pencairan(self):
        if self._context.get('active_id'):
            uudp_obj = self.env['uudp.pencairan']
            uudp = uudp_obj.browse(self._context.get('active_id'))
            uudps = uudp_obj.search([('pencairan_id','=',self._context.get('active_id')),('state','not in',('cancel','refuse'))])
            pencairans = 0.0
            for uu in uudps :
                #import pdb;pdb.set_trace()
                pencairans += sum(uu.ajuan_id.uudp_ids.mapped('sub_total'))
            pencairan_journal = 0.0
            for ent in uudp.journal_entry_ids :
                #import pdb;pdb.set_trace()
                pencairan_journal += ent.amount
            return uudp.nominal_ajuan - pencairan_journal - pencairans

    nominal = fields.Float(string="Nominal Pencairan", required=False)
    journal_id = fields.Many2one("account.journal", string="Journal", default=_get_default_journal_id)
    sisa_pencairan = fields.Float('Sisa Pencairan', default=_get_sisa_pencairan)
    date = fields.Date('Tanggal Pencairan')
    uudp_wizard_ids = fields.One2many("wizard.uudp.detail", "uudp_pencairan_id", string="Details", default=_get_default_uudp_details)

    def action_create_pencairan(self):
        self.ensure_one()
        total_cair = sum(self.uudp_wizard_ids.mapped('sub_total'))
        if total_cair > self.sisa_pencairan :
            raise UserError(_('Total pencairan ini melebihi sisa pencairan yang diizinkan !'))
        if total_cair <= 0.0  :
            raise UserError(_('Nominal pencairan tidak boleh 0!'))
        pencairan_obj = self.env['uudp.pencairan']
        if self.uudp_pencairan_id.ajuan_id.type == 'pengajuan' :
            myajuan = self.env['uudp'].search([('responsible_id','=',self.uudp_pencairan_id.ajuan_id.responsible_id.id),
                                                ('type','=','pengajuan'),
                                                ('id','!=',self.uudp_pencairan_id.ajuan_id.id),
                                                ('state', 'not in', ['refuse','cancel','done'])],
                                                order='id desc')
            if myajuan:
                amount = len(myajuan)
                if amount >= 1:
                    for m in myajuan:
                        if m.uudp_parent_id :
                            raise UserError(_('Ajuan sebelumnya (%s) belum ada pencairan !') % (m.name))
                        if self.uudp_pencairan_id.ajuan_id.uudp_parent_id :
                            if m.id == self.uudp_pencairan_id.ajuan_id.uudp_parent_id.id :
                                continue
                        raise ValidationError(_("Notes admin : ajuan (%s) akan di cancel, hubungi dulu administrator !") % (self.uudp_pencairan_id.ajuan_id.name))
                        #m.button_cancel()
                        #m.sudo().message_post(body=_('Cancel otomatis dari sistem karena terindikasi melalukan pengajuan ketika ajuan sebelumnya (%s) belum penyelesaian.') % (self.uudp_pencairan_id.ajuan_id.name,))

        details = []
        for uu in self.uudp_wizard_ids :
            details.append((0, 0, {'product_id': uu.product_id.id , 
                                            'partner_id': uu.partner_id.id,
                                            'store_id' : uu.store_id.id,
                                            'description' : uu.description,
                                            'qty' : uu.qty,
                                            'uom' : uu.uom,
                                            'unit_price' : uu.unit_price,
                                            'sub_total' : uu.sub_total,
                                            'total' : uu.sub_total,
                                            'state' : uu.state,
                                            'coa_debit' :uu.coa_debit.id }))
        new_ajuan = self.uudp_pencairan_id.ajuan_id.copy({ 'uudp_ids': details,
                                                           'total_pencairan' : total_cair,
                                                           'state' : self.uudp_pencairan_id.ajuan_id.state,
                                                           'uudp_parent_id' :  self.uudp_pencairan_id.ajuan_id.id})
        pencairan = pencairan_obj.create({'type' : 'once',
                                        'tgl_pencairan' : self.date,
                                        'pencairan_id' : self.uudp_pencairan_id.id,
                                        'company_id' : self.uudp_pencairan_id.company_id.id,
                                        'ajuan_id' : new_ajuan.id,
                                        'journal_id' : self.journal_id.id,
                                        'journal_id2' : self.journal_interco_id.id,
                                        'notes' : self.uudp_pencairan_id.notes,
                                        'sisa_pencairan_parsial' : self.sisa_pencairan - total_cair,
                                        'state' : 'confirm_once',
                                        'uudp_ids' :  [(6, 0, [new_ajuan.id])]})
        # total_pencairan_ids = []
        # for pc in self.uudp_pencairan_id.pencairan_ids :
        #     total_pencairan_ids.append(pc.id)
        # total_pencairan_ids.append(pencairan.id)
        # self.uudp_pencairan_id.write({'total_pencairan' : self.sisa_pencairan + total_cair})

        return new_ajuan



class WizardUUDPDetail(models.TransientModel):
    _name = "wizard.uudp.detail"

    @api.onchange('product_id')
    def onchange_product_id(self):
        product = self.product_id
        if product:
            #self.description = p.name
            if not self.uom :
                self.uom = product.uom_id.name
            if self.unit_price == 0.0 :
                self.unit_price = product.lst_price
            # if not self.coa_debit :
            self.coa_debit = product.property_account_expense_id.id

    uudp_pencairan_id = fields.Many2one("pencairan.wizard", string="Pencairan Wizard")
    product_id = fields.Many2one("product.product", string="Product",)
    partner_id = fields.Many2one("res.partner", string="Partner")
    store_id = fields.Many2one("res.partner", string="Store")
    description = fields.Char(string="Description", required=True)
    qty = fields.Float(string="Qty", required=True, default=1)
    uom = fields.Char(string="UoM", required=True, default="Pcs")
    unit_price = fields.Float(string="Unit Price", required=True, default=0)
    sub_total = fields.Float(string="Sub Total", compute="_calc_subtotal")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting'),
                              ('confirm_department', 'Confirm by Department'),
                              ('confirm_department1', 'Confirm by Department'),
                              ('confirm_finance', 'Confirm by Finance'),
                              ('confirm_accounting', 'Confirm by Accounting'),
                              ('confirm_hrd', 'Confirm by HRD'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled'),
                              ('refuse','Refused')], default='draft', required=True)

    coa_debit = fields.Many2one('account.account', string="Account")

    @api.depends('unit_price','qty')
    def _calc_subtotal(self):
        for rec in self:
            rec.sub_total = rec.unit_price * rec.qty

WizardUUDPDetail()