from odoo import _, api, fields, models
from datetime import date
import locale
from odoo.exceptions import UserError
from lxml import etree

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_id = fields.Many2one(comodel_name='freight.order', string='FO Number ID2')
    qty_delivered = fields.Integer(string='Qty Delivered')
    region = fields.Char(string='Region')
    pod = fields.Many2one(comodel_name='freight.port', string='POD')
    pol = fields.Many2one(comodel_name='freight.port', string='POL')
    load = fields.Many2one(comodel_name='freight.load', string='Load')
    # company_id = fields.Many2one('res.company','Company', default=lambda self:self.env.user.company_id)
    company_id = fields.Many2one(comodel_name='res.company', string='COmpany')
    