from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FreightOrderLine(models.Model):
    _name = 'freight.order.line'
    _description = 'freight order line'

    order_id = fields.Many2one('freight.order')
    # fo_number_id = fields.Many2one(comodel_name='freight.order', string='FO NUmber ID')
    