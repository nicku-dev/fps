from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fo_number = fields.Many2one(comodel_name='freight.order', string='FO Number')
