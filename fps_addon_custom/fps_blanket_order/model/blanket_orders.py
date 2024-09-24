from odoo import api, fields, models
from odoo.exceptions import ValidationError

class BlanketOrder(models.Model):
    _inherit = 'sale.blanket.order'

    file_contract = fields.Binary(string='File Contract')
