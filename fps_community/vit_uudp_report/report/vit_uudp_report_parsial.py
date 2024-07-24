# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError


class ReportParsial(models.AbstractModel):
    _name = 'report.vit_uudp_report.report_parsial'
    
    @api.model
    def render_html(self, docids, data=None):
        pencairan_ke = 0
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        journal_entries = self.env['account.move'].search([('uudp_pencairan_id','=',docs.uudp_pencairan_id.id)], order="date asc")
        for j in journal_entries:
            if j.date == docs.date:
                pencairan_ke += 1
                break;
            pencairan_ke +=1

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'pencairan_ke':pencairan_ke,
        }
        return self.env['report'].render('vit_uudp_report.report_parsial', docargs)