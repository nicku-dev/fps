from odoo import api, fields, models, tools, _


class accountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    uudp_pencairan_id = fields.Many2one("uudp.pencairan", string="UUDP Pencairan")
    terbilang = fields.Char(string='Terbilang', translate=True, readonly=True, states={'draft': [('readonly', False)]})

accountMove()


class accountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    state = fields.Selection(related='move_id.state', string="State",store=True)

accountMove()


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    show_on_uudp = fields.Boolean('Show on UUDP/Reim', help='Centang jika ingin muncul di UUDP/Reimberse')

AccountJournal()