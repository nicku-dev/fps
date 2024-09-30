from werkzeug import urls
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.tools.misc import format_date
from odoo.exceptions import ValidationError

from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES


class FreightOrder(models.Model):
    _name = 'freight.order'
    _description = 'Freight Order'

    sol_related_fo_field_ids = fields.One2many(
        comodel_name='sale.order.line',
        # inverse_name='fo_order_id',
        string='sol_related_fo_field_ids',
        compute='_compute_sol_related_fo_field',
        )
    
    # route_ids = fields.One2many('freight.routes', 'route_id')

    name = fields.Char('Name', default='New', readonly=True)
    shippment_type = fields.Many2one(comodel_name='freight.order.type', string='Shippment Type')
    shipper_id = fields.Many2one('res.partner', 'Shipper', help="Shipper's Details")
    consignee_id = fields.Many2one('res.partner', 'Consignee',help="Details of consignee")
    departure_time = fields.Datetime(string='Departure Time')
    arrival_time = fields.Datetime(string='Arrival Time')

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )

    line_ids = fields.One2many(
        "sale.order.line", 
        "order_id", 
        string="Order lines", copy=True
    )

    line_count = fields.Integer(
        string="Order Line count",
        compute="_compute_line_count",
        readonly=True,
    )

    state = fields.Selection([
            ("draft", "Draft"),
            ("submit", "LOAD"),
            ("confirm", "IN TRANSIT"),
            ("delivered", "DELIVERED"),
            ("documenting ", "DOCUMENTING TRIP"),
			('invoice', 'Invoiced'), 
            ("done", "Done"),
            ("cancel", "Cancel")]
            ,default='draft')
        
        
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        states=READONLY_FIELD_STATES,
    )

    # product_id = fields.Many2one(
    #     "product.product",
    #     related="line_ids.product_id",
    #     string="Product",
    # )
    # # pricelist_id = fields.Many2one(
    #     "product.pricelist",
    #     string="Pricelist",
    #     required=True,
    #     states=READONLY_FIELD_STATES,
    # )
    # currency_id = fields.Many2one("res.currency", 
    #                             #   related="pricelist_id.currency_id"
    #                               )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        copy=False,
        check_company=True,
        readonly=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    analytic_plan_id = fields.Many2one(
        comodel_name="account.analytic.plan",
        string="Analytic Plan",
        copy=False,
        check_company=True,
        readonly=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    payment_term_id = fields.Many2one(
        "account.payment.term",
        string="Payment Terms",
        states=READONLY_FIELD_STATES,
    )
    confirmed = fields.Boolean(copy=False)


    
    order_date = fields.Date(string='order_date')
    invoice_count = fields.Integer(compute='compute_count')
    so_count = fields.Integer(compute='compute_count')
    po_count = fields.Integer(compute='compute_count')
    # order_ids = fields.One2many('freight.order.line', 'order_id')
    agent_id = fields.Many2one('res.partner', 'Agent Muat', required=True,
                               help="Details of agent")
    agent_muat_id = fields.Many2one('res.partner', 'Agent Muat', required=True,
                               help="Details of agent")
    agent_bongkar_id = fields.Many2one('res.partner', 'Agent Bongkar', required=True,
                            help="Details of agent")

    expected_date = fields.Date('Expected Date')
    # track_ids = fields.One2many('freight.track', 'track_id')
    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Nama Kapal')
    koordinator_kapal_id = fields.Many2one('hr.employee', 'Name', 
                                        #    required=True,
                                            help="Koordinator Kapal (employe)")
    fo_region_id = fields.Many2one('freight.port', 'region',  help='Region')
    # sol_ids = fields.One2many(comodel_name='sale.order.line', inverse_name='fo_number_2_id', string='fo_id')
    timesheet_ids = fields.One2many(comodel_name='freight.timesheet', inverse_name='timesheet_id', string='Timesheet')
    carriage_ids = fields.One2many(comodel_name='freight.carriage', inverse_name='carriage_id', string='CARRIAGE')
    costing_ids = fields.One2many(comodel_name='freight.costing', inverse_name='costing_id', string='COSTING')
    profitability_ids = fields.One2many(comodel_name='freight.profitability', inverse_name='profitability_id', string='profitability')
    route_sol_ids = fields.One2many(comodel_name='sale.order.line', inverse_name='id', string='Freight Route')


    ###
    user_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        states=READONLY_FIELD_STATES,
    )

    # Fields use to filter in tree view
    original_uom_qty = fields.Float(
        string="Original quantity",
        # compute="_compute_uom_qty",
        # search="_search_original_uom_qty",
        default=0.0,
    )
    ordered_uom_qty = fields.Float(
        string="Ordered quantity",
        compute="_compute_uom_qty",
        search="_search_ordered_uom_qty",
        default=0.0,
    )
    invoiced_uom_qty = fields.Float(
        string="Invoiced quantity",
        compute="_compute_uom_qty",
        search="_search_invoiced_uom_qty",
        default=0.0,
    )
    remaining_uom_qty = fields.Float(
        string="Remaining quantity",
        compute="_compute_uom_qty",
        search="_search_remaining_uom_qty",
        default=0.0,
    )
    delivered_uom_qty = fields.Float(
        string="Delivered quantity",
        compute="_compute_uom_qty",
        search="_search_delivered_uom_qty",
        default=0.0,
    )


    ### SBO
    # line_ids = fields.One2many("sale.order.line", "id", string="Order lines", copy=True)
    # line_ids = fields.One2many("freight.order.line", "order_id", string="Order lines", copy=True)

    route_id = fields.Many2one(comodel_name='freight.routes', string='Rute')
    route_code_id = fields.Char(related='route_id.route_code', string='Rute ID')
    freight_port_id = fields.Many2one('freight.port', 'POL / Source Location')
    region_id = fields.Char(related='route_id.region_id', string='Region')
    source_loc_id = fields.Many2one(related='route_id.source_loc', string='source_loc')
    destination_loc_id = fields.Many2one(related='route_id.destination_loc', string='destination_loc')


    # route_code = fields.Char(string='Kode Rute', required=True)
    # destination_loc = fields.Char(related='source_loc.destination_loc', string= 'POD / Destination Location')

    
    @api.model
    def create(self, vals):
        """Create Sequence"""
        sequence_code = 'freight.order.sequence'
        vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code)
        return super(FreightOrder, self).create(vals)
    

    # def name_get(self):
    #     result = []
    #     if self.env.context.get("from_sale_order"):
    #         for record in self:
    #             res = "[%s]" % record.order_id.name
    #             if record.date_schedule:
    #                 formatted_date = format_date(record.env, record.date_schedule)
    #                 res += " - {}: {}".format(_("Date Scheduled"), formatted_date)
    #             res += " ({}: {} {})".format(
    #                 _("remaining"),
    #                 record.remaining_uom_qty,
    #                 record.product_uom.name,
    #             )
    #             result.append((record.id, res))
    #         return result
    #     return super().name_get()
    
    @api.depends("line_ids")
    def _compute_line_count(self):
        self.line_count = len(self.mapped("line_ids"))

    def action_view_sale_blanket_order_line(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "freight_order.act_open_freight_order_lines_view_tree"
        )
        lines = self.mapped("line_ids")
        if len(lines) > 0:
            action["domain"] = [("id", "in", lines.ids)]
        return action

    def action_cancel(self):
        """Cancel the record"""
        if self.state == 'draft' and self.state == 'submit':
            self.state = 'cancel'
        else:
            raise ValidationError("You can't cancel this order")

    def get_invoice(self):
        """View the invoice"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('ref', '=', self.name)],
            'context': "{'create': False}"
        }
    
    def get_so_related(self):
        """View the invoice"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('fo_number', '=', self.name)],
            'context': "{'create': False}"
        }
    
    def get_sol_related(self):
        """View the invoice"""
        self.ensure_one()
        lines = self.mapped("line_ids")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order Line',
            'view_mode': 'tree,form',
            'res_model': 'sale.order.line',
            # 'domain': [('id', 'in', self.line_ids.ids)],
            'domain': [('fo_id', '=', self.name)],
            # 'domain': [('fo_number', '=', self.name)],
            # 'domain': [('order_id', '=', self.name)],
            # 'domain': [('order_id.name', '=', self.name)],
            'context': "{'create': False}"
        }
        # print("-------------------",self)

    

    # @api.one
    def _compute_sol_related_fo_field(self):
        ### get recordset of related object, for example with search (or whatever you like):
        related_recordset = self.env["sale.order.line"].search([("fo_id", "in", self.name)])
        self.sol_related_fo_field_ids = related_recordset  

    @api.depends('name')
    def compute_count(self):
        """Compute custom clearance and account move's count"""
        for rec in self:
            if rec.env['account.move'].search([('ref', '=', rec.name)]):
                rec.invoice_count = rec.env['account.move'].search_count(
                    [('ref', '=', rec.name)])
            else:
                rec.invoice_count = 0
            if rec.env['sale.order'].search([('fo_number', '=', rec.name)]):
                rec.so_count = rec.env['sale.order'].search_count(
                    [('fo_number', '=', rec.name)])
            else:
                rec.so_count = 0
            if rec.env['sale.order.line'].search([('fo_id', '=', rec.name)]):
                rec.line_count = rec.env['sale.order.line'].search_count(
                    [('fo_id', 'in', rec.name)])
            else:
                rec.line_count = 0
            # if rec.env['purchase.order'].search([('fo_id', '=', rec.name)]):
            #     rec.po_count = rec.env['purchase.order'].search_count(
            #         [('po_count', 'in', rec.name)])
            # else:
            #     rec.line_count = 0
                
    def action_submit(self):
        """Submitting order"""
        for rec in self:
            rec.state = 'submit'
            # base_url = self.env['ir.config_parameter'].sudo().get_param(
            #     'web.base.url')
            # Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})

            # mail_content = _('Hi %s,<br>'
            #                  'The Freight Order %s is Submitted'
            #                  '<div style = "text-align: center; '
            #                  'margin-top: 16px;"><a href = "%s"'
            #                  'style = "padding: 5px 10px; font-size: 12px; '
            #                  'line-height: 18px; color: #FFFFFF; '
            #                  'border-color:#875A7B;text-decoration: none; '
            #                  'display: inline-block; margin-bottom: 0px; '
            #                  'font-weight: 400;text-align: center; '
            #                  'vertical-align: middle; cursor: pointer; '
            #                  'white-space: nowrap; background-image: none; '
            #                  'background-color: #875A7B; '
            #                  'border: 1px solid #875A7B; border-radius:3px;">'
            #                  'View %s</a></div>'
            #                  ) % (rec.agent_id.name, rec.name, Urls, rec.name)
            # email_to = self.env['res.partner'].search([
            #     ('id', 'in', (self.shipper_id.id, self.consignee_id.id,
            #                   self.agent_id.id))])
            # for mail in email_to:
            #     main_content = {
            #         'subject': _('Freight Order %s is Submitted') % self.name,
            #         'author_id': self.env.user.partner_id.id,
            #         'body_html': mail_content,
            #         'email_to': mail.email
            #     }
            #     mail_id = self.env['mail.mail'].create(main_content)
            #     mail_id.mail_message_id.body = mail_content
            #     mail_id.send()

    def action_confirm(self):
        """Confirm order"""
        for rec in self:
            rec.state = 'confirm'
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})
            mail_content = _('Hi %s,<br> '
                            'The Freight Order %s is Confirmed '
                            '<div style = "text-align: center; '
                            'margin-top: 16px;"><a href = "%s"'
                            'style = "padding: 5px 10px; '
                            'font-size: 12px; line-height: 18px; '
                            'color: #FFFFFF; border-color:#875A7B; '
                            'text-decoration: none; '
                            'display: inline-block; '
                            'margin-bottom: 0px; font-weight: 400;'
                            'text-align: center; '
                            'vertical-align: middle; '
                            'cursor: pointer; white-space: nowrap; '
                            'background-image: none; '
                            'background-color: #875A7B; '
                            'border: 1px solid #875A7B; '
                            'border-radius:3px;">'
                            'View %s</a></div>'
                            ) % (rec.agent_id.name, rec.name,
                                          Urls, rec.name)
            email_to = self.env['res.partner'].search([
                ('id', 'in', (self.shipper_id.id,
                                self.consignee_id.id, self.agent_id.id))])
            for mail in email_to:
                main_content = {
                    'subject': _('Freight Order %s is Confirmed') % self.name,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': mail.email
                }
                mail_id = self.env['mail.mail'].create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.send()

    def action_done(self):
        """Mark order as done"""
        for rec in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})

            mail_content = _('Hi %s,<br>'
                             'The Freight Order %s is Completed'
                             '<div style = "text-align: center; '
                             'margin-top: 16px;"><a href = "%s"'
                             'style = "padding: 5px 10px; font-size: 12px; '
                             'line-height: 18px; color: #FFFFFF; '
                             'border-color:#875A7B;text-decoration: none; '
                             'display: inline-block; '
                             'margin-bottom: 0px; font-weight: 400;'
                             'text-align: center; vertical-align: middle; '
                             'cursor: pointer; white-space: nowrap; '
                             'background-image: none; '
                             'background-color: #875A7B; '
                             'border: 1px solid #875A7B; border-radius:3px;">'
                             'View %s</a></div>'
                             ) % (rec.agent_id.name, rec.name, Urls, rec.name)
            email_to = self.env['res.partner'].search([
                ('id', 'in', (self.shipper_id.id, self.consignee_id.id,
                              self.agent_id.id))])
            for mail in email_to:
                main_content = {
                    'subject': _('Freight Order %s is completed') % self.name,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': mail.email
                }
                mail_id = self.env['mail.mail'].create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.send()
            self.state = 'done'

            for line in rec.order_ids:
                line.container_id.state = 'available'

    @api.depends("line_ids")
    def _compute_line_count(self):
        self.line_count = len(self.mapped("line_ids"))


    #### BO
    # def _compute_uom_qty(self):
    #     for bo in self:
    #         bo.original_uom_qty = sum(bo.mapped("line_ids.original_uom_qty"))
    #         bo.ordered_uom_qty = sum(bo.mapped("line_ids.ordered_uom_qty"))
    #         bo.invoiced_uom_qty = sum(bo.mapped("line_ids.invoiced_uom_qty"))
    #         bo.delivered_uom_qty = sum(bo.mapped("line_ids.delivered_uom_qty"))
    #         bo.remaining_uom_qty = sum(bo.mapped("line_ids.remaining_uom_qty"))



# class FreightOrderLine(models.Model):
#     _name = 'freight.order.line'
#     _description = 'Freight Order Line'

    # @api.depends(
    #     "original_uom_qty",
    #     "price_unit",
    #     "taxes_id",
    #     "order_id.partner_id",
    #     "product_id",
    #     # "currency_id",
    # )
    # def _compute_amount(self):
    #     for line in self:
    #         price = line.price_unit
    #         taxes = line.taxes_id.compute_all(
    #             price,
    #             # line.currency_id,
    #             line.original_uom_qty,
    #             product=line.product_id,
    #             partner=line.order_id.partner_id,
    #         )
    #         line.update(
    #             {
    #                 "price_tax": sum(
    #                     t.get("amount", 0.0) for t in taxes.get("taxes", [])
    #                 ),
    #                 "price_total": taxes["total_included"],
    #                 "price_subtotal": taxes["total_excluded"],
    #             }
    #         )


    # name = fields.Char("Description", tracking=True)
    # sequence = fields.Integer()
    # order_id = fields.Many2one("freight.order", required=True, ondelete="cascade")
    # product_id = fields.Many2one(
    #     "product.product",
    #     string="Product",
    #     domain=[("sale_ok", "=", True)],
    # )
    # product_uom = fields.Many2one("uom.uom", string="Unit of Measure")
    # price_unit = fields.Float(string="Price", digits="Product Price")
    # taxes_id = fields.Many2many(
    #     "account.tax",
    #     string="Taxes",
    #     domain=["|", ("active", "=", False), ("active", "=", True)],
    # )
    
    ### B.O.L
    # date_schedule = fields.Date(string="Scheduled Date")
    # original_uom_qty = fields.Float(
    #     string="Original quantity", default=1, digits="Product Unit of Measure"
    # )
    # ordered_uom_qty = fields.Float(
    #     string="Ordered quantity", compute="_compute_quantities", store=True
    # )
    # invoiced_uom_qty = fields.Float(
    #     string="Invoiced quantity", compute="_compute_quantities", store=True
    # )
    # remaining_uom_qty = fields.Float(
    #     string="Remaining quantity", compute="_compute_quantities", store=True
    # )
    # remaining_qty = fields.Float(
    #     string="Remaining quantity in base UoM",
    #     compute="_compute_quantities",
    #     store=True,
    # )
    # delivered_uom_qty = fields.Float(
    #     string="Delivered quantity", compute="_compute_quantities", store=True
    # )
    # sale_lines = fields.One2many(
    #     "sale.order.line",
    #     "blanket_order_line",
    #     string="Sale order lines",
    #     readonly=True,
    #     copy=False,
    # )
    # company_id = fields.Many2one(
    #     related="order_id.company_id", store=True, index=True, precompute=True
    # )

    # currency_id = fields.Many2one("res.currency", related="order_id.currency_id")
    # partner_id = fields.Many2one(related="order_id.partner_id", string="Customer")
    # user_id = fields.Many2one(related="order_id.user_id", string="Responsible")
    # payment_term_id = fields.Many2one(
    #     related="order_id.payment_term_id", string="Payment Terms"
    # )
    # pricelist_id = fields.Many2one(related="order_id.pricelist_id", string="Pricelist")

    # price_subtotal = fields.Monetary(
    #     # compute="_compute_amount", 
    #     string="Subtotal", store=True
    # )
    # price_total = fields.Monetary(compute="_compute_amount", string="Total", store=True)
    # price_tax = fields.Float(compute="_compute_amount", string="Tax", store=True)
    # display_type = fields.Selection(
    #     [("line_section", "Section"), ("line_note", "Note")],
    #     default=False,
    #     help="Technical field for UX purpose.",
    # )

    # def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
    #     """Retrieve the price before applying the pricelist
    #     :param obj product: object of current product record
    #     :param float qty: total quentity of product
    #     :param tuple price_and_rule: tuple(price, suitable_rule) coming
    #            from pricelist computation
    #     :param obj uom: unit of measure of current order line
    #     :param integer pricelist_id: pricelist id of sale order"""
    #     # Copied and adapted from the sale module
    #     PricelistItem = self.env["product.pricelist.item"]
    #     field_name = "lst_price"
    #     currency_id = None
    #     product_currency = None
    #     if rule_id:
    #         pricelist_item = PricelistItem.browse(rule_id)
    #         if pricelist_item.pricelist_id.discount_policy == "without_discount":
    #             while (
    #                 pricelist_item.base == "pricelist"
    #                 and pricelist_item.base_pricelist_id
    #                 and pricelist_item.base_pricelist_id.discount_policy
    #                 == "without_discount"
    #             ):
    #                 price, rule_id = pricelist_item.base_pricelist_id.with_context(
    #                     uom=uom.id
    #                 )._get_product_price_rule(product, qty, uom)
    #                 pricelist_item = PricelistItem.browse(rule_id)

    #         if pricelist_item.base == "standard_price":
    #             field_name = "standard_price"
    #         if pricelist_item.base == "pricelist" and pricelist_item.base_pricelist_id:
    #             field_name = "price"
    #             product = product.with_context(
    #                 pricelist=pricelist_item.base_pricelist_id.id
    #             )
    #             product_currency = pricelist_item.base_pricelist_id.currency_id
    #         currency_id = pricelist_item.pricelist_id.currency_id

    #     product_currency = (
    #         product_currency
    #         or (product.company_id and product.company_id.currency_id)
    #         or self.env.company.currency_id
    #     )
    #     if not currency_id:
    #         currency_id = product_currency
    #         cur_factor = 1.0
    #     else:
    #         if currency_id.id == product_currency.id:
    #             cur_factor = 1.0
    #         else:
    #             cur_factor = currency_id._get_conversion_rate(
    #                 product_currency, currency_id
    #             )

    #     product_uom = product.uom_id.id
    #     if uom and uom.id != product_uom:
    #         # the unit price is in a different uom
    #         uom_factor = uom._compute_price(1.0, product.uom_id)
    #     else:
    #         uom_factor = 1.0

    #     return product[field_name] * uom_factor * cur_factor, currency_id.id

    # def _get_display_price(self, product):
    #     # Copied and adapted from the sale module
    #     self.ensure_one()
    #     pricelist = self.order_id.pricelist_id
    #     partner = self.order_id.partner_id
    #     if self.order_id.pricelist_id.discount_policy == "with_discount":
    #         return product.with_context(pricelist=pricelist.id).lst_price
    #     final_price, rule_id = pricelist._get_product_price_rule(
    #         self.product_id, self.original_uom_qty or 1.0, self.product_uom
    #     )
    #     context_partner = dict(
    #         self.env.context, partner_id=partner.id, date=fields.Date.today()
    #     )
    #     base_price, currency_id = self.with_context(
    #         **context_partner
    #     )._get_real_price_currency(
    #         self.product_id,
    #         rule_id,
    #         self.original_uom_qty,
    #         self.product_uom,
    #         pricelist.id,
    #     )
    #     if currency_id != pricelist.currency_id.id:
    #         currency = self.env["res.currency"].browse(currency_id)
    #         base_price = currency.with_context(**context_partner).compute(
    #             base_price, pricelist.currency_id
    #         )
    #     # negative discounts (= surcharge) are included in the display price
    #     return max(base_price, final_price)

    # @api.onchange("product_id", "original_uom_qty")
    # def onchange_product(self):
    #     precision = self.env["decimal.precision"].precision_get(
    #         "Product Unit of Measure"
    #     )
    #     if self.product_id:
    #         name = self.product_id.name
    #         if not self.product_uom:
    #             self.product_uom = self.product_id.uom_id.id
    #         if self.order_id.partner_id and float_is_zero(
    #             self.price_unit, precision_digits=precision
    #         ):
    #             self.price_unit = self._get_display_price(self.product_id)
    #         if self.product_id.code:
    #             name = "[{}] {}".format(name, self.product_id.code)
    #         if self.product_id.description_sale:
    #             name += "\n" + self.product_id.description_sale
    #         self.name = name

            # fpos = self.order_id.fiscal_position_id
            # if self.env.uid == SUPERUSER_ID:
            #     company_id = self.env.company.id
            #     self.taxes_id = fpos.map_tax(
            #         self.product_id.taxes_id.filtered(
            #             lambda r: r.company_id.id == company_id
            #         )
            #     )
            # else:
            #     self.taxes_id = fpos.map_tax(self.product_id.taxes_id)

    # @api.depends(
    #     "sale_lines.order_id.state",
    #     "sale_lines.blanket_order_line",
    #     "sale_lines.product_uom_qty",
    #     "sale_lines.product_uom",
    #     "sale_lines.qty_delivered",
    #     "sale_lines.qty_invoiced",
    #     "original_uom_qty",
    #     "product_uom",
    # )
    # def _compute_quantities(self):
    #     for line in self:
    #         sale_lines = line.sale_lines
    #         line.ordered_uom_qty = sum(
    #             sl.product_uom._compute_quantity(sl.product_uom_qty, line.product_uom)
    #             for sl in sale_lines
    #             if sl.order_id.state != "cancel" and sl.product_id == line.product_id
    #         )
    #         line.invoiced_uom_qty = sum(
    #             sl.product_uom._compute_quantity(sl.qty_invoiced, line.product_uom)
    #             for sl in sale_lines
    #             if sl.order_id.state != "cancel" and sl.product_id == line.product_id
    #         )
    #         line.delivered_uom_qty = sum(
    #             sl.product_uom._compute_quantity(sl.qty_delivered, line.product_uom)
    #             for sl in sale_lines
    #             if sl.order_id.state != "cancel" and sl.product_id == line.product_id
    #         )
    #         line.remaining_uom_qty = line.original_uom_qty - line.ordered_uom_qty
    #         line.remaining_qty = line.product_uom._compute_quantity(
    #             line.remaining_uom_qty, line.product_id.uom_id
    #         )

    # def _validate(self):
    #     try:
    #         for line in self:
    #             assert (
    #                 not line.display_type and line.price_unit > 0.0
    #             ) or line.display_type, _("Price must be greater than zero")
    #             assert (
    #                 not line.display_type and line.original_uom_qty > 0.0
    #             ) or line.display_type, _("Quantity must be greater than zero")
    #     except AssertionError as e:
    #         raise UserError(e) from e
