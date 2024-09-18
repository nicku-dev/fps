from odoo import _, api, fields, models
from datetime import date
import locale
from odoo.exceptions import UserError
from lxml import etree

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_bill_lading = fields.Integer(string='Qty B/L')
    qty_difference = fields.Integer(string='Qty Difference')
    freight_order_id = fields.Many2one(comodel_name='freight.order', string='FO Number ID2')
    # freight_order_id = fields.Char(related='order_id.name', string='FO Number ID2')
    sol_routes_ids = fields.One2many(comodel_name='freight.routes', inverse_name='sol_routes_id',string='FO Number ID3')
    qty_delivered = fields.Integer(string='Qty Delivered')
    is_claim_susut = fields.Boolean(string='Claim Susut')
    
    # region = fields.Char(string='Region')
    pod = fields.Many2one(comodel_name='freight.port', string='POD')
    pol = fields.Many2one(comodel_name='freight.port', string='POL')
    load = fields.Many2one(comodel_name='freight.load', string='Load')
    company_id = fields.Many2one('res.company','Company', default=lambda self:self.env.user.company_id)
    # company_id = fields.Many2one(comodel_name='res.company', string='COmpany')
    fo_id = fields.Char(related='order_id.name', string='FO_ID', tracking=True)

