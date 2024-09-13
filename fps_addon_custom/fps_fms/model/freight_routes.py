from odoo import fields, models

class FreightRoutes(models.Model):
    _name = 'freight.routes'
    _description = 'Freight Routes'

    route_id = fields.Many2one(comodel_name='freight.order', string='Route')
    name = fields.Char('Nama', required=True)
    active = fields.Boolean('Active', default=True)
    route_code = fields.Char(string='Kode Rute', required=True)
    # region = fields.Many2one('freight_port.region', 'Region')
    region = fields.Char(related='source_loc.region', string='Region')
    # region_id = fields.Many2one('freight.port', 'Region')
    source_loc = fields.Many2one('freight.port', 'POL / Source Location')
    destination_loc = fields.Many2one('freight.port', 'POD / Destination Location')
