# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    force_invoiced = fields.Boolean(
        help="When you set this field, the sales order will be considered as "
        "fully invoiced, even when there may be ordered or delivered "
        "quantities pending to invoice.",
        readonly=True,
        states={"done": [("readonly", False)], "sale": [("readonly", False)]},
        tracking=20,
        copy=False,
    )

    @api.depends("force_invoiced")
    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        self.filtered(
            lambda so: so.force_invoiced and so.state in ("sale", "done")
        ).update({"invoice_status": "invoiced"})
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id.force_invoiced")
    def _compute_untaxed_amount_to_invoice(self):
        force_invoiced = self.filtered(lambda x: x.order_id.force_invoiced)
        force_invoiced.update({"untaxed_amount_to_invoice": 0.0})
        not_forced = self - force_invoiced
        return super(SaleOrderLine, not_forced)._compute_untaxed_amount_to_invoice()
