from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FreightorderType(models.Model):
    _name = 'freight.order.type'
    _description = 'Freight Order Type'
    _rec_name = 'name'

    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean('Active', default=True)
