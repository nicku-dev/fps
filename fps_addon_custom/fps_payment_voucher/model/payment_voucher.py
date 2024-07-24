from odoo import api, fields, models, exceptions, _
import datetime
from odoo.exceptions import UserError, AccessError, ValidationError
# from odoo.addons.terbilang import terbilang
import logging
_logger = logging.getLogger(__name__)

class PaymentVoucher(models.Model):
    _name = 'payment.voucher'
    _description = "Payment Voucher"
    _order = 'name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Code", default="New", readonly=True)
    user_id = fields.Many2one("res.users", string="Employee", default=lambda self: self.env.user, store=True, required=True, track_visibility='onchange',)
    department_id = fields.Many2one("hr.department", string="Department", track_visibility='onchange',)
    company_id = fields.Many2one("res.company", string="Company",default=lambda self: self.env['res.company']._company_default_get(), required=True)
    type = fields.Selection([('pengajuan', 'Pengajuan'), 
                             ('penyelesaian', 'Penyelesaian'), 
                             ('reimberse', 'Reimberse'),],string='Type', required=True, track_visibility='onchange',)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting Department'),
                              ('confirm_department', 'Confirmed Department'),
                              ('confirm_department1', 'Waiting HRD'),
                              ('confirm_hrd', 'Confirmed HRD'),
                              ('pending', 'Pending'),
                              ('confirm_finance', 'Confirmed Finance'),
                              ('confirm_accounting', 'Confirmed Accounting'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled'),
                              ('refuse','Refused')], default='draft', required=True, index=True, track_visibility='onchange',)
    payment_voucher_ids = fields.One2many("payment.voucher.detail", inverse_name="payment_voucher_id", track_visibility='onchange',)
    coa_debit = fields.Many2one("account.account", string="Debit Account")
    coa_kredit = fields.Many2one("account.account", string="Credit Account")
    ajuan_id = fields.Many2one('payment.voucher', string="Ajuan", domain="[('type','=','pengajuan')]")
    total_ajuan = fields.Float(string="Total Ajuan", track_visibility='onchange',)
    # total_ajuan_penyelesaian = fields.Float(string="Total Pencairan", related="ajuan_id.total_pencairan", readonly=True, track_visibility='onchange',)
    need_driver = fields.Boolean(string="Perjalanan Dinas?", track_visibility='onchange',)
    # need_driver_penyelesaian = fields.Boolean(string="Penyelesaian Perjalanan Dinas?", related="ajuan_id.need_driver",store=True)
    selesai = fields.Boolean(string="Selesai")
    journal_id = fields.Many2one("account.journal", string="Journal", track_visibility='onchange')# default=_default_journal)
    journal_entry_id = fields.Many2one("account.move", string="Journal Entry")
    difference = fields.Many2one("account.account", string="Difference Account", track_visibility='onchange')
    difference_notes = fields.Char("Difference Notes", track_visibility='onchange')
    responsible_id = fields.Many2one("res.users", string="Responsible", track_visibility='onchange')
    cara_bayar = fields.Selection([('cash', 'Cash'), 
                                   ('transfer', 'Transfer'),],string='Cara Bayar', track_visibility='onchange',)
    bank_id = fields.Many2one("res.bank", string="Bank", track_visibility='onchange',)
    no_rekening = fields.Char(string="Nomor Rekening", track_visibility='onchange',)
    atas_nama = fields.Char(string="Atas Nama", track_visibility='onchange',)
    notes = fields.Text(string="Notes", track_visibility='onchange')
    total_pencairan = fields.Float(string="Total Pencairan", track_visibility='onchange',)
    type_pencairan = fields.Selection([('once', 'Once'), 
                                       ('parsial', 'Parsial'),],string='Type Pencairan')
    date = fields.Date(string="Required Date", required=True, default=fields.Datetime.now, track_visibility='onchange',)
    terbilang = fields.Char(string='Terbilang', translate=True, readonly=True, states={'draft': [('readonly', False)]})
    is_user_pencairan = fields.Boolean(compute="check_validity")
    pencairan_id = fields.Many2one("payment.voucher.pencairan","Pencairan")
    tgl_pencairan = fields.Date("Tanggal Pencairan",)# related="pencairan_id.tgl_pencairan", store=True)
    sisa_penyelesaian = fields.Float("Sisa Penyelesaian", compute="_get_sisa_penyelesaian", store=True,track_visibility='onchange',)
    end_date = fields.Date(string="End Date",  track_visibility='onchange',)
    by_pass_selisih = fields.Boolean("By Pass Different Amount",  track_visibility='onchange')
    selesai_id = fields.Many2one('payment.voucher','Selesai ID',compute="search_input_penyelesaian")
    penyelesaian_id = fields.Many2one('payment.voucher','Penyelesaian')# store ke db
    tgl_penyelesaian = fields.Date("Tgl Penyelesaian")

    @api.model
    def create(self, vals):
        """Create Sequence"""
        sequence_code = 'payment.voucher.pengajuan'
        vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code)
        return super(PaymentVoucher, self).create(vals)


class PaymentVoucherDetail(models.Model):
    _name = "payment.voucher.detail"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    payment_voucher_id = fields.Many2one("payment.voucher", string="Nomor Payment Voucher", track_visibility='onchange',)
    product_id = fields.Many2one("product.product", string="Product", track_visibility='onchange',)
    partner_id = fields.Many2one("res.partner", string="Partner", track_visibility='onchange')
    store_id = fields.Many2one("res.partner", string="Store", track_visibility='onchange')
    description = fields.Char(string="Description", required=True, track_visibility='onchange',)
    qty = fields.Float(string="Qty", required=True, default=1, track_visibility='onchange',)
    uom = fields.Char(string="UoM", required=True, track_visibility='onchange', default="Pcs")
    unit_price = fields.Float(string="Unit Price", required=True, default=0, track_visibility='onchange',)
    sub_total = fields.Float(string="Sub Total", compute="_calc_sub_total", store=True)
    total = fields.Float(string="Total", track_visibility='onchange',)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting Department'),
                              ('confirm_department', 'Confirmed Department'),
                              ('confirm_department1', 'Waiting HRD'),
                              ('confirm_hrd', 'Confirmed HRD'),
                              ('pending', 'Pending'),
                              ('confirm_finance', 'Confirmed Finance'),
                              ('confirm_accounting', 'Confirmed Accounting'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled'),
                              ('refuse','Refused')], default='draft', required=True, index=True, track_visibility='onchange',)
    coa_debit = fields.Many2one('account.account', string="Account", track_visibility='onchange')