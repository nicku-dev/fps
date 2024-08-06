from odoo import api, fields, models, tools, _


class accountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    payment_requisition_pencairan_id = fields.Many2one("payment.requisition.pencairan", string="Payment Requisition Pencairan")
    terbilang = fields.Char(string='Terbilang', translate=True, readonly=True, states={'draft': [('readonly', False)]})

class accountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    state = fields.Selection(related='move_id.state', string="State",store=True)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    show_on_payment_requisition = fields.Boolean('Show on Payment Requisition atau di Reimburse', help='Centang jika ingin muncul di Payment Requisition atau di Reimberse')
