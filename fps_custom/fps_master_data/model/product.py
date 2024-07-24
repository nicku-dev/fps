# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from datetime import date
import locale
from odoo.exceptions import UserError
from lxml import etree

class ProductCategory(models.Model):
    _inherit = 'product.category'

    ec_category_code = fields.Char(string='ec_CategoryCode')
    description = fields.Char(string='Description')
    source_data = fields.Char(string='Descriptiom', default='Indonesia')
    ec_category_type = fields.Char(string='ec_CategoryType')
