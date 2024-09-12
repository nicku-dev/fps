from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    file_npwp = fields.Binary(string='File NPWP')
    # file_npwp = fields.Binary(string='File NPWP')
    file_skt = fields.Binary(string='File SKT')
    file_spkp = fields.Binary(string='File SPKP')
    file_siupal = fields.Binary(string='File SIUPAL')



