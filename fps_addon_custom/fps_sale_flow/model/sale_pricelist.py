
from werkzeug import urls
from odoo import api, fields, models, _
from datetime import datetime

class SaleMdPricelist(models.Model):
    _name = 'sale.md.pricelist'
    _description = 'Sale MD Pricelist'

    name = fields.Char('Name')
    create_date = fields.Date('Create Date', default=datetime.today())
    price_region = fields.Char(string='Region')
    pol = fields.Char(string='POL')
    pod = fields.Char(string='POD')
    load = fields.Char(string='LOAD')
    unit_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        compute='_compute_currency_id', store=True, readonly=False, precompute=True,
        help="The payment's currency.")
    