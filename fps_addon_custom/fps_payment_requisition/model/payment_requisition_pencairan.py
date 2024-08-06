from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError, AccessError, ValidationError
# from odoo.addons.terbilang import terbilang

class PaymentRequisitionPencairan(models.Model):
    _name = 'payment.requisition.pencairan'
    _order = 'name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nomor Pencairan", readonly=True, default="New")
    tgl_pencairan = fields.Date(string="Tanggal Pencairan", required=True, default=fields.Datetime.now, track_visibility='onchange',)
    user_id = fields.Many2one("res.users", string="User", default=lambda self: self.env.user)
    payment_requisition_ids = fields.Many2many("payment.requisition", string="Detail Ajuan", domain="[('state','=','confirm_finance'),('type','=','pengajuan')]", track_visibility='onchange',)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm_once', 'Confirm'),
                              ('confirm_parsial', 'Confirm'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled'),
                              ('refuse','Refused')], default='draft', required=True, index=True, track_visibility='onchange',)
    journal_id = fields.Many2one("account.journal", string="Journal", required=True, track_visibility='onchange',)
    coa_kredit = fields.Many2one("account.account", string="Account", 
                                #  related="journal_id.default_credit_account_id", 
                                 help="Credit Account", track_visibility='onchange')
    journal_entry_id = fields.Many2one("account.move", string="Journal Entry", track_visibility='onchange',)
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env['res.company']._company_default_get())
    type = fields.Selection([('parsial', 'Parsial'), 
                             ('once', 'At Once'),],string='Type Pencairan', required=True)
    journal_entry_ids = fields.One2many("account.move", string="Journal Entries", inverse_name="payment_requisition_pencairan_id", track_visibility='onchange',)
    ajuan_id = fields.Many2one('payment.requisition', string="Ajuan", track_visibility='onchange',)
    nominal_ajuan = fields.Float(String="Nominal Ajuan", related="ajuan_id.total_ajuan")
    notes = fields.Text(string="Notes", track_visibility='onchange',)
    sisa_pencairan_parsial = fields.Float(string="Sisa Pencairan Parsial")
    total_pencairan = fields.Float(string="Total Pencairan", compute="get_total_pencairan")

    @api.depends('payment_requisition_ids.state','journal_entry_ids.state')
    def get_total_pencairan(self):
        for rec in self:
            total = 0
            if rec.payment_requisition_ids:
                for u in rec.payment_requisition_ids:
                    total += u.total_ajuan
                rec.total_pencairan = total
    
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('payment.requisition.pencairan') or '/'
        vals['name'] = seq
        return super(PaymentRequisitionPencairan, self).create(vals)