from werkzeug import urls
from odoo import api, fields, models, _

from odoo.exceptions import ValidationError

import requests, json



class ApiEcataloc(models.Model):
    _name = 'api.ecataloc'
    _description = 'Api Ecataloc'

    name = fields.Char(string='Name')
    is_master_data = fields.Boolean(string='Master Data')
    