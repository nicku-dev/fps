# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018  ADHOC SA  (http://www.vitraining.com)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from collections import defaultdict
import math
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    @api.depends('ref', 'name')
    def name_get(self):
        result = []
        for res in self:
            name = res.name
            if res.ref :
                name = '['+res.ref+'] '+name
            result.append((res.id, name))
        return result

    @api.multi
    def write(self, vals):
        #import pdb;pdb.set_trace()
        old_tag = self.account_analytic_tag_id.id
        if 'account_analytic_tag_id' in vals :
            if not vals['account_analytic_tag_id'] :
                vals['account_analytic_tag_id'] = old_tag
        if 'ref' in vals :
            self.display_name = '['+vals['ref']+'] '+self.name
        res = super(ResPartner, self).write(vals)
        return res

    account_analytic_tag_id = fields.Many2one("account.analytic.tag", string="Analytic Tag",track_visibility='always')

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if not res.display_name:
            name = res.name
            if res.ref:
                name = '['+res.ref+'] '+name
            res.display_name = name  
        return res

ResPartner()


class Followers(models.Model):
    _inherit = 'mail.followers'


    # handle error ketika save account move sebagian user : Error, a partner cannot follow twice the same object
    @api.model
    def create(self, vals):
        if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
            dups = self.env['mail.followers'].sudo().search([('res_model', '=',vals.get('res_model')),
                                               ('res_id', '=', vals.get('res_id')),
                                               ('partner_id', '=', vals.get('partner_id'))])
            if len(dups):
                for p in dups:
                    p.sudo().unlink()
        res = super(Followers, self).create(vals)
        return res

Followers()