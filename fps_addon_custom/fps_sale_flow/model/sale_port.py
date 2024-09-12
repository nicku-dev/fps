from odoo import fields, models, api, _


class SaleMdPort(models.Model):
    _name = 'sale.md.port'
    _description = 'Sales Master Data for Port (Pelabuhan)'
    _rec_name = 'port_name'

    port_name = fields.Char('Port Name', required=True)
    region = fields.Char(string='REGION', required=True)
    code = fields.Char('Code', required=True)
    state_id = fields.Many2one('res.country.state',domain="[('country_id', '=', country_id)]")
    # country_id = fields.Many2one('res.country', default='1',required=True)
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self.env['res.country'].browse([(100)]))
    active = fields.Boolean('Active', default=True)




class SaleMdPricing(models.Model):
    _name = 'sale.md.pricing'

    name = fields.Char('Name', required=True)
    volume = fields.Float('Volume Price', required=True)
    weight = fields.Float('Weight Price', required=True)


class SaleMdRoutes(models.Model):
    _name = 'sale.md.routes'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)

class SaleMdPricelist(models.Model):
    _name = 'sale.md.pricelist'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)

    
    


