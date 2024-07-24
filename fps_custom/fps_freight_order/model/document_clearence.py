
from werkzeug import urls
from odoo import api, fields, models, _


class DocumentClearance(models.Model):
    _name = 'document.clearance'
    _description = 'Document Clearance'

    name = fields.Char('Name', compute='_compute_name')
    freight_id = fields.Many2one('freight.order', required=True)
    date = fields.Date('Date')
    agent_id = fields.Many2one('res.partner', 'Agent', required=True)
    loading_port_id = fields.Many2one('freight.port', string="Loading Port")
    discharging_port_id = fields.Many2one('freight.port',
                                          string="Discharging Port")
    line_ids = fields.One2many('document.clearance.line', 'line_id')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('done', 'Done')], default='draft')

    @api.depends('freight_id')
    def _compute_name(self):
        """Compute the name of Document Clearance"""
        for rec in self:
            if rec.freight_id:
                rec.name = 'DOC - ' + str(rec.freight_id.name)
            else:
                rec.name = 'DCC - '

    @api.onchange('freight_id')
    def _onchange_freight_id(self):
        """Getting default values for loading and discharging port"""
        for rec in self:
            rec.date = rec.freight_id.order_date
            rec.loading_port_id = rec.freight_id.loading_port_id
            rec.discharging_port_id = rec.freight_id.discharging_port_id
            rec.agent_id = rec.freight_id.agent_id

    def action_confirm(self):
        """Send mail to inform agents to Document clearance is confirmed"""
        for rec in self:
            rec.name = 'CC' \
                       ' - ' + rec.freight_id.name
            rec.state = 'confirm'
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            Urls = urls.url_join(base_url, 'web#id=%(id)s&model=Document.clearance&view_type=form' % {'id': self.id})
            Urls_ = urls.url_join(base_url, 'web#id=%(id)s&model=freight.order&view_type=form' % {'id': self.freight_id.id})

            mail_content = _('Hi %s,<br>'
                             'The Document Clearance %s is confirmed'
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
                             ) % (rec.agent_id.name, rec.name, Urls,
                                  rec.name, Urls_, self.freight_id.name)
            main_content = {
                'subject': _('Document Clerance For %s') % self.freight_id.name,
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': rec.agent_id.email,
            }
            mail_id = self.env['mail.mail'].create(main_content)
            mail_id.mail_message_id.body = mail_content
            mail_id.send()

    def action_revision(self):
        """Creating Document revision"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Received/Delivered',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'Document.clearance.revision.wizard',
            'context': {
                'default_Document_id': self.id
            }
        }

    def get_revision(self):
        """Getting details of Document revision"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Document Revision',
            'view_mode': 'tree,form',
            'res_model': 'Document.clearance.revision',
            'domain': [('clearance_id', '=', self.id)],
            'context': "{'create': False}"
        }


class DocumentClearanceLine(models.Model):
    _name = 'Document.clearance.line'
    _description = 'Document Clearance Line'

    name = fields.Char('Document Name')
    document = fields.Binary(string="Documents", store=True, attachment=True)
    line_id = fields.Many2one('Document.clearance')


class DocumentClearanceRevision(models.Model):
    _name = 'Document.clearance.revision'
    _description = 'Document Clearance Revision'

    name = fields.Char('Name')

    name = fields.Char()
    reason = fields.Text()
    clearance_id = fields.Many2one('document.clearance')
