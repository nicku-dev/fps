# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from datetime import date
import locale
from odoo.exceptions import UserError
from lxml import etree

class SaleShipmentType(models.Model):
    _name = 'sale.shipment.type'
    _description = 'Sale Shippment Type'
    _rec_name = 'name'

    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean('Active', default=True)
