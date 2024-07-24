

from odoo import fields, models


class FreightPort(models.Model):
    _name = 'freight.port'

    name = fields.Char('Port Name', required=True)
    region = fields.Char('Region', required=True)
    code = fields.Char('Code', required=True)
    state_id = fields.Many2one('res.country.state',
                               domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', required=True)
    active = fields.Boolean('Active', default=True)
    is_pol = fields.Boolean('Is POL', default=True)
    load_ids = fields.Many2many(comodel_name='freight.load', string='LOAD')
    
    land = fields.Boolean('Land')
    air = fields.Boolean('Air')
    water = fields.Boolean('Water')


class FreightPricing(models.Model):
    _name = 'freight.price'

    name = fields.Char('Name', required=True)
    volume = fields.Float('Volume Price', required=True)
    weight = fields.Float('Weight Price', required=True)


class FreightRoutes(models.Model):
    _name = 'freight.routes'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    land_sale = fields.Float('Sale Price for Land', required=True)
    air_sale = fields.Float('Sale Price for Air', required=True)
    water_sale = fields.Float('Sale Price for Water', required=True)

class FreightLoad(models.Model):
    _name = 'freight.load'

    name = fields.Char('Name')
    description = fields.Char('Description')
    code = fields.Char('Code')
