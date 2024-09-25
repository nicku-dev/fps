from odoo import models, fields, api, _

class FreightOrder(models.Model):
    _inherit = 'freight.order'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    analytic_plan_id = fields.Many2one('account.analytic.plan', string="Analytic Plan")

    def _create_analytic_account(self):
        """
        This function will automatically create an analytic account based on the sales order number.
        """
        for order in self:
            # Optionally, assign a default analytic plan if needed
            analytic_plan = self.env['account.analytic.plan'].search([('is_default', '=', True)], limit=1)
            if analytic_plan:
                order.analytic_plan_id = analytic_plan.id
            
            # Create an analytic account if it doesn't already exist
            analytic_account = self.env['account.analytic.account'].create({
                'name': order.name,
                'partner_id': order.partner_id.id,
                'company_id': order.company_id.id,
                'plan_id': order.analytic_plan_id.id,
            })
            
            # Assign the analytic account to the sales order
            order.analytic_account_id = analytic_account.id


    @api.model
    def create(self, vals):
        """
        Override the create method to trigger the automatic creation of the analytic account.
        """
        order = super(FreightOrder, self).create(vals)
        order._create_analytic_account()
        return order
