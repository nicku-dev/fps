from werkzeug import urls
from odoo import api, fields, models, _

from odoo.exceptions import ValidationError

import requests, json

class Contacts(models.Model):
    _inherit = 'res.partner'

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
    
    def get_customer(self):
            url = "http://10.100.1.26:1002/api/Vendor/GetAllVendorByParameters?pageSize=100&pageNumber=1"
            
            payload = {}
            headers = {
                'Authorization': '{{authorizationHeader}}'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            print(response.text)
            data =response.json()
            # print(data,"dataaaaaaa")
            x= self.env['res.partner'].sudo().create({
                  'id':data['partner_id'],
                  'email':data['email'],
                  'name':data['name'],
                  'phone':data['phone']})
            print(x)

    def get_customer1(self):
        url = "https://reqres.in/api/users?page=2"
        
        payload = {}
        headers = {
            'Authorization': '{{authorizationHeader}}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)
        data =response.json()
        # print(data,"dataaaaaaa")
        x= self.env['res.partner'].sudo().create({
                'parent_id':data['partner_id'],
                'type':data['contact'],
                'email':data['email'],
                'phone':data['phone'],
                # 'name':
                })
        print(x)