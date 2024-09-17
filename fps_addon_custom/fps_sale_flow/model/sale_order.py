# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from datetime import date
import locale
from odoo.exceptions import UserError
from lxml import etree

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    LOCKED_FIELD_STATES = {
        state: [('readonly', True)]
        for state in {'done', 'cancel'}
    }

    READONLY_FIELD_STATES = {
        state: [('readonly', True)]
        for state in {'sale', 'done', 'cancel'}
    }
    
    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('new', "NEW"),
            ('sent', "Quotation Sent"),
            ('sale', "Sales Order"),
            ('done', "Locked"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    
    ### SO DATA 
    shippment_type_id = fields.Many2one(comodel_name='sale.shipment.type', 
                                        # default='normal', 
                                        string='Shippment Type',
                                        tracking=True,
                                        # required=True
                                        )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True, readonly=False, change_default=True, index=True,
        tracking=1,
        states=READONLY_FIELD_STATES,
        domain="[('type', 'not in', ('private', 'delivery', 'other', 'invoice')), ('company_id', 'in', (False, company_id))]")
    
    shipper_id = fields.Many2one(
        comodel_name='res.partner',
        string="Pengirim/Shipper",
        required=True, readonly=False, change_default=True, index=True,
        tracking=1,
        states=READONLY_FIELD_STATES,
        domain="[('type', 'not in', ('private', 'delivery', 'other', 'invoice')), ('company_id', 'in', (False, company_id))]")
    
    consignee_id = fields.Many2one(
        comodel_name='res.partner',
        string="Penerima/Consignee",
        required=True, readonly=False, change_default=True, index=True,
        tracking=1,
        states=READONLY_FIELD_STATES,
        help="02. PEMILIK MUATAN (“PIHAK KEDUA”) :",
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id))]")
  
    ### SPAL DATA

    spal_number = fields.Char(string='SPAL Number')
    spal_date = fields.Char(string='SPAL DATE')
    company_id = fields.Many2one('res.company','Company', default=lambda self:self.env.user.company_id)
    bendera_spal = fields.Char(string='Bendera', default='Indonesia')
    jumlah_muatan = fields.Float(string='Jumlah Muatan/Kargo')
    kondisi_kontrak_muatan = fields.Selection(string='Kondisi Kontrak Muatan / Voyage Condition', selection=[('F.I.O.S.T', 'F.I.O.S.T'), ('other', 'other'),])
    uang_tambang = fields.Char(string='Uang Tambang / Freight Kapal')
    tanggal_kesediaan_muat = fields.Date(string='Kesediaan Untuk Muat / Lay Can')
    cara_pembayaran = fields.Char(string='Cara Pembayaran', default='100% Pada Saat Kapal Sandar di Pelabuhan Tujuan Dan Setelah Bongkar')
    pengiriman_barang = fields.Char(string='Pengiriman Barang', default='As Order di Shipping Instruction')
    penerima_barang = fields.Char(string='Penerima Barang', default='As Order di Shipping Instruction')
    purchase_date = fields.Date(string='PO Date')
    po_number = fields.Char(string='PO Number', help='Referensi PO Number data dari E-Cataloc')
    contract_number = fields.Char(string='Contract Number', help='Referensi Nomor Kontrak Perjanjian dengan Customer. data dari E-Cataloc')
    
    # freight_routes_id = fields.Many2one("freight.routes", string="Freight Order ID4", required=True)



    # 
    # Relational
    # partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    # property_id = fields.Many2one("estate.property", string="Property", required=True)
    # For stat button:
    # property_type_id = fields.Many2one(
    #     "estate.property.type", related="property_id.property_type_id", string="Property Type", store=True
    # )

    
    # analytic_plan_id = fields.Many2one('account_analytic_plan','id')
    # analytic_plan_id = fields.Many2one('account.analytic.plan', 'name')
    

    commitment_date = fields.Datetime(
        string="Delivery Date", copy=False,
        states=LOCKED_FIELD_STATES,
        tracking=True,
        help="This is the delivery date promised to the customer. "
             "If set, the delivery order will be scheduled based on "
             "this date rather than product lead times.")

    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_partner_invoice_id',
        store=True, readonly=False, required=True, precompute=True,
        states=LOCKED_FIELD_STATES,
        tracking=True,
        domain="[('type', 'in', ('contact', 'invoice')), '|', ('parent_id', '=', partner_id), ('id', '=', partner_id)]")
    
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery Address",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False, required=True, precompute=True,
        states=LOCKED_FIELD_STATES,
        tracking=True,
        domain="[('type', 'in', ('contact', 'delivery')), '|', ('parent_id', '=', partner_id), ('id', '=', partner_id)]")

    # sales_type = fields.Selection([('freight_charter', 'Freight Charter'),
    #                                ('time_charter', 'Time Charter'),
    #                                ('heavy_equipment_transport', 'Heavy Equipment Transport'),
    #                                ('normal', 'Normal')], default='normal', string='Sales Type', required=True)

  
    loading_duration = fields.Float(string='Lama Loading (hari)')
    unloading_duration = fields.Float(string='Lama Unloading (hari)')
    harga_termasuk = fields.Char(string='Harga Termasuk')
    harga_tidak_termasuk = fields.Char(string='Harga Tidak Termasuk')
    agent_id = fields.Many2one('res.partner', 'Agent', required=False,
                               help="Keagenan Kapal / POL & POD Agency")
    nama_kapal = fields.Many2one('fleet.vehicle', 'Fleet', required=True, help="Keagenan Kapal / POL & POD Agency")
    account_bank_number_id = fields.Many2one('res.partner.bank', 'Account Number', help="Nomor Rekening Customer yang akan keluar di SPAL")
    si_number = fields.Char(string='Shipping Instruction Number')
    si_date = fields.Date(string='Shipping Instruction Date')
    voyage_condition = fields.Selection(string='Kondisi Kontrak Muatan/ Voyage Condition', selection=[('FIOST', 'F.I.O.S.T'), ('', ''),])
    asuransi_kapal = fields.Char(string='Asuransi Kapal', default='Diatur Oleh Pihak Pertama')
    asuransi_muatan = fields.Char(string='Asuransi Muatan', default='Diatur Oleh Pihak Kedua')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        compute='_compute_currency_id', store=True, readonly=False, precompute=True,
        help="The payment's currency.")
    demurage = fields.Monetary(currency_field='currency_id')
    fo_number = fields.Many2one(comodel_name='freight.order', string='FO Number')
    spal_format = fields.Selection(string='SPAL FORMAT', selection=[('normal','Normal'), ('fch', 'Freight Charter'), ('time_based', 'Time Based Charter'),('fame', 'F.A.M.E'),])
    is_hide = fields.Boolean(string='HIDE', compute="_compute_hide")
    so_pod = fields.Many2one(comodel_name='freight.port', string='POD')
    so_pol = fields.Many2one(comodel_name='freight.port', string='POL')
    toleransi_susut = fields.Float(string='Toleransi Susut')
    fo_order_lines = fields.One2many('sale.order.line', compute='_compute_fo_order_lines', string='FO Order Lines')


    @api.onchange('spal_format')
    def _compute_hide(self):
       if self.spal_format == 'normal':
           self.is_hide = True
       else:
           self.is_hide = False

    def _compute_fo_order_lines(self):
        for order in self:
            if order.fo_number:
                order.fo_order_lines = self.env['sale.order.line'].search([
                    ('order_id.fo_number', '=', order.fo_number)
                ]) 