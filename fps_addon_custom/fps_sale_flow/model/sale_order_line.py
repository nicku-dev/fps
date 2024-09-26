from odoo import _, api, fields, models
from datetime import date
import locale
from odoo.exceptions import UserError
from lxml import etree

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fo_order_id = fields.Many2one(comodel_name='freight.order', string='FO Number')
    qty_delivered = fields.Integer(string='Qty Delivered')
    region_id = fields.Many2one(comodel_name='freight.port', string='POD')
    pod_id = fields.Many2one(comodel_name='freight.port', string='POD')
    pol_id = fields.Many2one(comodel_name='freight.port', string='POL')
    load_id = fields.Many2one(comodel_name='freight.load', string='Load')
    company_id = fields.Many2one('res.company','Company', default=lambda self:self.env.user.company_id)
    fo_id = fields.Many2one(related='order_id.fo_number', string='FO Number', store = True, tracking=True)
    # original_uom_qty = fields.Float(string="Original quantity", default=0.0)
        # compute="_compute_uom_qty",
        # search="_search_original_uom_qty",
    
    # region = fields.Char(string='Region')
    # sol_routes_ids = fields.One2many(comodel_name='freight.routes',string='FO Number ID3')

    # Fields use to filter in tree view
    ordered_uom_qty = fields.Float(
        string="Ordered quantity",
        compute="_compute_uom_qty",
        search="_search_ordered_uom_qty",
        default=0.0,
    )
    invoiced_uom_qty = fields.Float(
        string="Invoiced quantity",
        compute="_compute_uom_qty",
        search="_search_invoiced_uom_qty",
        default=0.0,
    )
    remaining_uom_qty = fields.Float(
        string="Remaining quantity",
        compute="_compute_uom_qty",
        search="_search_remaining_uom_qty",
        default=0.0,
    )
    delivered_uom_qty = fields.Float(
        string="Delivered quantity",
        compute="_compute_uom_qty",
        search="_search_delivered_uom_qty",
        default=0.0,
    )