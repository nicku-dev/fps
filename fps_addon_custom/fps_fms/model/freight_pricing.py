from odoo import fields, models

class FreightPricing(models.Model):
    _name = 'freight.price'

    name = fields.Char('Name', required=True)
    volume = fields.Float('Volume Price', required=True)
    weight = fields.Float('Weight Price', required=True)