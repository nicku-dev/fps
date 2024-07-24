from odoo import fields, api, models
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.addons import decimal_precision as dp

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    penyelesaian_id = fields.Many2one(comodel_name='uudp', string='Penyelesaian', ondelete='restrict', copy=False)
    reimburse_id = fields.Many2one(comodel_name='uudp', string='Reimburse', ondelete='restrict', copy=False)
