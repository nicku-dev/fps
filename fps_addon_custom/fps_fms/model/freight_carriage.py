from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Freightcarriage(models.Model):
    _name = 'freight.carriage'
    _description = 'Freight Carriage'

    carriage_id = fields.Many2one('freight.order')
    carriage_so = fields.Many2one(comodel_name='sale.order', string='Sales Order')
    load = fields.Many2one(comodel_name='freight.load', string='Load')
    qty_so = fields.Integer(string='Qty SO')
    qty_bl = fields.Integer(string='Qty B/L')
    qty_final = fields.Integer(string='Qty Final')
    qty_difference = fields.Integer(string='Qty Difference')
    toleransi_claim = fields.Integer(string='% Toleransi Klaim ')
    claim_susut = fields.Integer(string='Claim Susut')
    uom = fields.Many2one(comodel_name='uom.uom', string='UoM')
    




class FreightCosting(models.Model):
    _name = 'freight.costing'
    _description = 'Freight Costing'

    costing_id = fields.Many2one(comodel_name='freight.order', string='Vendor Bill')
    fo_vendor_bill = fields.Char(string='Vendor Bill')
    vendor = fields.Many2one(comodel_name='res.partner', string='Vendor')
    product = fields.Char(string='Product')
    keterangan = fields.Char(string='Keterangan')
    qty_user = fields.Float(string='Qty Used')
    uom = fields.Many2one(comodel_name='uom.uom', string='UoM')
    price_unit = fields.Float(string='Price Unit')
    taxes = fields.Float(string='Taxes')
    total = fields.Float(string='Total')





class FreightProfitability(models.Model):
    _name = 'freight.profitability'
    _description = 'Freight Profitability'

    profitability_id = fields.Many2one(comodel_name='freight.order', string='profitability')
    invoice = fields.Char(string='Invoice/vendor bill')
    customer_fo = fields.Many2one(comodel_name='res.partner', string='Customer')
    product_fo = fields.Many2one(comodel_name='product.template', string='Product')
    keterangan = fields.Char(string='Keterangan')
    uom = fields.Many2one(comodel_name='uom.uom', string='UoM')
    price_unit = fields.Float(string='Price Unit')
    taxes = fields.Float(string='Taxes')
    total = fields.Float(string='Total')
    
    
    
    
    