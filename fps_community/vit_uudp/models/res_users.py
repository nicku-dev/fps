from odoo import fields, api, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def name_get(self):
        res = []
        for x in self:
            name = '['+x.login+'] '+x.name
            res.append((x.id, name))
        return res

ResUsers()