from werkzeug import urls
from odoo import api, fields, models, _

from odoo.exceptions import ValidationError

import requests, json, xlsxwriter



class Apiconfig(models.Model):
    _name = 'api.config'
    _description = 'API Configuration'

    base_url = fields.Char(string='BASE URL')
    user = fields.Char(string='User')    

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_base_url = fields.Char('API URL', help="Setup API Url sebagai Base URL untuk integrasi dengan API",
                                  default='https://reqres.in/api/users?page=2', config_parameter='api_base_url')