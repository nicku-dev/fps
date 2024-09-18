from odoo import _, api, fields, models
from datetime import date
import locale
from odoo.exceptions import UserError
from lxml import etree

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    freight_order_id = fields.Many2one(comodel_name='freight.order', string='FO Number ID2')
    # freight_order_id = fields.Char(related='order_id.name', string='FO Number ID2')
    sol_routes_ids = fields.One2many(comodel_name='freight.routes', inverse_name='sol_routes_id',string='FO Number ID3')
    qty_delivered = fields.Integer(string='Qty Delivered')
    # region = fields.Char(string='Region')
    pod = fields.Many2one(comodel_name='freight.port', string='POD')
    pol = fields.Many2one(comodel_name='freight.port', string='POL')
    load = fields.Many2one(comodel_name='freight.load', string='Load')
    company_id = fields.Many2one('res.company','Company', default=lambda self:self.env.user.company_id)
    # company_id = fields.Many2one(comodel_name='res.company', string='COmpany')
    fo_id = fields.Many2one(related='order_id.fo_number', string='FO Number', store = True, tracking=True)
    # fo_sol = fields.Char(related='id.fo_number', string='FO SOL ID', tracking=True)
