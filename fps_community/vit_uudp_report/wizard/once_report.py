# -*- coding: utf-8 -*-

from odoo import api, fields, models

class OnceWizard(models.TransientModel):
    _name = "once.wizard"
    _description = "Once wizard"

    def _get_active_uudp(self):
        context = self.env.context
        if context.get('active_model') == 'uudp':
            return context.get('active_id', False)
        return False

    def wizard_close(self):
        return {'type': 'ir.actions.act_window_close'}

    uudp_id = fields.Many2one('uudp', string="UUDP", default=_get_active_uudp)

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['uudp_id'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['uudp_id'])[0])
        return self.env['report'].get_action(self, 'vit_uudp_report.report_once', data=data)