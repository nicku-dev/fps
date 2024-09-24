from odoo import models, fields

class AnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    is_default = fields.Boolean(string='Is Default Plan', default=False)
