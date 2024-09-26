from odoo import fields, models

class FreightRoutes(models.Model):
    _name = 'freight.routes'
    _description = 'Freight Routes'

    name = fields.Char('Nama', required=True)
    active = fields.Boolean('Active', default=True)
    route_code = fields.Char(string='Kode Rute', required=True)
    region_id = fields.Char(related='source_loc.region', string='Region')
    source_loc = fields.Many2one('freight.port', 'POL / Source Location')
    destination_loc = fields.Many2one('freight.port', 'POD / Destination Location')

    # Relational (for inline view)
    # route_ids = fields.One2many(comodel_name='sale.order', inverse_name='freight_routes_id', string='Freight Route')
    # route_sol_ids = fields.One2many(comodel_name='sale.order.line', inverse_name='order_id', string='Freight Route')
    routes_id = fields.Many2one(comodel_name='freight.order', string='Route')
    route_id = fields.Many2one(comodel_name='freight.order', string='Route1')
    # sol_routes_id = fields.Many2one(comodel_name='sale.order.line', string='Route')