from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FreightOrderType(models.Model):
    _name = 'freight.order.document'
    _description = 'Freight Order Document'

    name = fields.Char('Name', default='New', readonly=True)
    code = fields.Char('Code')
    active = fields.Boolean('Active', default=True)
