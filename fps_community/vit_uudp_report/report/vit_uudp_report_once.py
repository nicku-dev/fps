# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError


class ReportOnce(models.AbstractModel):
    _name = 'report.vit_uudp_report.report_once'
    
    @api.model
    def render_html(self, docids, data=None):
        # import pdb;pdb.set_trace();
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        sql = "SELECT uudp_pencairan.tgl_pencairan AS date FROM uudp_uudp_pencairan_rel AS urel INNER JOIN uudp ON urel.uudp_id = uudp.id INNER JOIN uudp_pencairan ON urel.uudp_pencairan_id = uudp_pencairan.id WHERE urel.uudp_id = %s"

        cr = self.env.cr
        cr.execute(sql, ([(docs.id)]))
        result = self.env.cr.dictfetchall()
        tanggal = False
        for tgl in result:
            tanggal = tgl['date']
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'tgl_pencairan': tanggal,
        }
        return self.env['report'].render('vit_uudp_report.report_once', docargs)