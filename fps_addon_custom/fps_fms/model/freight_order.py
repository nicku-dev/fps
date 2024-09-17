from werkzeug import urls
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.tools.misc import format_date
from odoo.exceptions import ValidationError

from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES


class FreightOrder(models.Model):
    _name = 'freight.order'
    _description = 'Freight Order'

    name = fields.Char('Name', default='New', readonly=True)
    shippment_type = fields.Many2one(comodel_name='freight.order.type', string='Shippment Type')
    shipper_id = fields.Many2one('res.partner', 'Shipper', required=True,help="Shipper's Details")
    consignee_id = fields.Many2one('res.partner', 'Consignee',help="Details of consignee")
    departure_time = fields.Datetime(string='Departure Time')
    arrival_time = fields.Datetime(string='Arrival Time')
    line_ids = fields.One2many(
        "freight.order.line", "order_id", string="Order lines", copy=True
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
    order_date = fields.Date(string='order_date')
    invoice_count = fields.Integer(compute='compute_count')
    so_count = fields.Integer(compute='compute_count')
    # order_ids = fields.One2many('freight.order.line', 'order_id')
    route_ids = fields.One2many('freight.routes', 'route_id')
    agent_id = fields.Many2one('res.partner', 'Agent', required=True,
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

    # route_id = fields.Many2one(comodel_name='freight.route', string='Rute')
    
    @api.model
    def create(self, vals):
        """Create Sequence"""
        sequence_code = 'freight.order.sequence'
        vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code)
        return super(FreightOrder, self).create(vals)
    

    def name_get(self):
        result = []
        if self.env.context.get("from_sale_order"):
            for record in self:
                res = "[%s]" % record.order_id.name
                if record.date_schedule:
                    formatted_date = format_date(record.env, record.date_schedule)
                    res += " - {}: {}".format(_("Date Scheduled"), formatted_date)
                res += " ({}: {} {})".format(
                    _("remaining"),
                    record.remaining_uom_qty,
                    record.product_uom.name,
                )
                result.append((record.id, res))
            return result
        return super().name_get()
    
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
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order Line',
            'view_mode': 'tree,form',
            'res_model': 'sale.order.line',
            # 'domain': [('order_id', '=', self.name)],
            # 'domain': [('order_id.name', '=', self.name)],
            'context': "{'create': False}"
        }
        print("-------------------",self)

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
            # if rec.env['sale.order.line'].search([('fo_number', '=', rec.name)]):
            #     rec.so_count = rec.env['sale.order.line'].search_count(
            #         [('fo_number', '=', rec.name)])
            # else:
            #     rec.so_line_count = 0
                
    def action_submit(self):
        """Submitting order"""
        for rec in self:
            rec.state = 'submit'
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            Urls = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.id})

            mail_content = _('Hi %s,<br>'
                             'The Freight Order %s is Submitted'
                             '<div style = "text-align: center; '
                             'margin-top: 16px;"><a href = "%s"'
                             'style = "padding: 5px 10px; font-size: 12px; '
                             'line-height: 18px; color: #FFFFFF; '
                             'border-color:#875A7B;text-decoration: none; '
                             'display: inline-block; margin-bottom: 0px; '
                             'font-weight: 400;text-align: center; '
                             'vertical-align: middle; cursor: pointer; '
                             'white-space: nowrap; background-image: none; '
                             'background-color: #875A7B; '
                             'border: 1px solid #875A7B; border-radius:3px;">'
                             'View %s</a></div>'
                             ) % (rec.agent_id.name, rec.name, Urls, rec.name)
            email_to = self.env['res.partner'].search([
                ('id', 'in', (self.shipper_id.id, self.consignee_id.id,
                              self.agent_id.id))])
            for mail in email_to:
                main_content = {
                    'subject': _('Freight Order %s is Submitted') % self.name,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': mail.email
                }
                mail_id = self.env['mail.mail'].create(main_content)
                mail_id.mail_message_id.body = mail_content
                mail_id.send()

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




class FreightOrderLine(models.Model):
    _name = 'freight.order.line'
    _description = 'Freight Order Line'

    name = fields.Char("Description", tracking=True)
    sequence = fields.Integer()
    order_id = fields.Many2one("freight.order", required=True, ondelete="cascade")
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain=[("sale_ok", "=", True)],
    )
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure")
    price_unit = fields.Float(string="Price", digits="Product Price")
    taxes_id = fields.Many2many(
        "account.tax",
        string="Taxes",
        domain=["|", ("active", "=", False), ("active", "=", True)],
    )
    date_schedule = fields.Date(string="Scheduled Date")