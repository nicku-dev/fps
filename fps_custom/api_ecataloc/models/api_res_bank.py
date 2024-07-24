from werkzeug import urls
from odoo import api, fields, models, _

import requests, json

class InheritResBank(models.Model):
    _inherit = 'res.bank'
    _description = 'Inherit Res Bank from Ecataloc'

    ec_id = fields.Char('Ecataloc ID')
    ec_code = fields.Char('Ecataloc CODE')
    ec_is_delete = fields.Char('Ecataloc Is Delete')

    def action_test1(self):       
            data = requests.get(url="http://10.100.1.26:1002/api/Bank/GetAllBank").content
            resp = json.loads(data)
            i = 0
            for item in resp["data"]:
                i += 1
                print(i, " # ", item["code"], " # ", item["name"])
                if i <= 200:
                    Partner = self.env['res.bank']
                    new = Partner.create(
                        {
                        'name': item["name"], 
                        'bic': item["code"],
                         }
                        )
                    print(new, " is created !!!")

    # @api.model
    # def create(self, vals_list):
    #     email = vals_list.get('email', None)
    #     if email:
    #         partner = self.env['res.partner'].search([('email', '=', email)], limit=1)
    #         if partner:
    #             raise ValidationError('User already exists.')
    #     return super(Contacts, self).create(vals_list)
    # 