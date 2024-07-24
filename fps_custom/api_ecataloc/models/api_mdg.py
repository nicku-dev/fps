from werkzeug import urls
from odoo import api, fields, models, _

from odoo.exceptions import ValidationError

import requests, json, xlsxwriter



class ApiMdg(models.Model):
    _name = 'api.mdg'
    _description = 'Api Mdg'

    mdg_id = fields.Char()
    mdg_email = fields.Char()
    mdg_first_name = fields.Char()
    mdg_last_name = fields.Char()
    mdg_avatar = fields.Char()
    phone = fields.Char()
    value_unit_price = fields.Integer()
    value_total_price = fields.Float(string='Value price')
    description = fields.Text()
    ec_id = fields.Char('Ecataloc ID')
    ec_code = fields.Char('Ecataloc CODE')
    ec_is_delete = fields.Char('Ecataloc Is Delete')

    def get_customer1(self):
        res = requests.get('https://reqres.in/api/users?page=1')
        response = res.text
        response_json = json.loads(response)
        data = response_json['data']
        for d in data:
            self.env['api.mdg'].create({
                'mdg_id':d['id'],
                'mdg_first_name':d['first_name'],
                'mdg_last_name':d['last_name'],
                'mdg_email':d['email'],
                'mdg_avatar':d['avatar']
            })

        print(d)
    def get_customer2(self):
        url = "https://reqres.in/api/users?page=2"
        
        payload = {}
        headers = {
            'Authorization': '{{authorizationHeader}}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)
        data =response.json()
        print(data,"dataaaaaaa")
        x=self.env['mdg.api'].create({
        'ref':data['mdg_id'],
        })
        x= self.env['mdg.api'].sudo().create({
                'ref':data['mdg_id'],
                'type':data['contact'],
                'email':data['email'],
                'phone':data['phone'],
                'name':data['first_name'],
                # 'name':
                })
        print(x)