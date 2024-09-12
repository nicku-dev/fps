from odoo import http

class Sale(http.Controller):

    @http.route("/fpsrepo/sales")
    def list(self, **kwargs):
        sale = http.request.env["sale.order"]
        sales = sale.search([])
        return http.request.render(
            "fps_sale_flow.sale_order",
            {"sale": sales}
        )
