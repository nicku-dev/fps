from odoo import fields, models

class FreightRoutes(models.Model):
    _name = 'freight.routes'
    _description = 'Freight Routes'

    route_id = fields.Many2one(comodel_name='freight.order', string='Route')
    sol_routes_id = fields.Many2one(comodel_name='sale.order.line', string='Route')
    name = fields.Char('Nama', required=True)
    active = fields.Boolean('Active', default=True)
    route_code = fields.Char(string='Kode Rute', required=True)
    # region = fields.Many2one('freight_port.region', 'Region')
    region = fields.Char(related='source_loc.region', string='Region')
    # region_id = fields.Many2one('freight.port', 'Region')
    source_loc = fields.Many2one('freight.port', 'POL / Source Location')
    destination_loc = fields.Many2one('freight.port', 'POD / Destination Location')

    # Relational (for inline view)
    # route_ids = fields.One2many(comodel_name='sale.order', inverse_name='freight_routes_id', string='Freight Route')
    # route_sol_ids = fields.One2many(comodel_name='sale.order.line', inverse_name='order_id', string='Freight Route')
    

    # Computed (for stat button)
    # order_count = fields.Integer(string="Order Line Count", compute="_compute_offer")
    # order_ids = fields.Many2many("sale.order.line", string="Order Line", compute="_compute_offer")

    def _compute_order(self):
        # This solution is quite complex. It is likely that the trainee would have done a search in
        # a loop.
        data = self.env["estate.property.offer"].read_group(
            [("property_id.state", "!=", "canceled"), ("property_type_id", "!=", False)],
            ["ids:array_agg(id)", "property_type_id"],
            ["property_type_id"],
        )
        mapped_count = {d["property_type_id"][0]: d["property_type_id_count"] for d in data}
        mapped_ids = {d["property_type_id"][0]: d["ids"] for d in data}
        for prop_type in self:
            prop_type.offer_count = mapped_count.get(prop_type.id, 0)
            prop_type.offer_ids = mapped_ids.get(prop_type.id, [])

    # ---------------------------------------- Action Methods -------------------------------------

    def action_view_offers(self):
        res = self.env.ref("estate.estate_property_offer_action").read()[0]
        res["domain"] = [("id", "in", self.offer_ids.ids)]
        return res
