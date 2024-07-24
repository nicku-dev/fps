# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ParsialWizard(models.TransientModel):
    _name = "parsial.wizard"
    _description = "Parsial wizard"
   
    def _get_active_journal_entry(self):
        context = self.env.context
        if context.get('active_model') == 'account.move':
            return context.get('active_id', False)
        return False

    journal_entry_id = fields.Many2one('account.move', string='journal Entry', default=_get_active_journal_entry)

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['journal_entry_id'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['journal_entry_id'])[0])
        return self.env['report'].get_action(self, 'vit_uudp_report.report_parsial', data=data)