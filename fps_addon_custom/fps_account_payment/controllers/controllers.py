# -*- coding: utf-8 -*-
# from odoo import http


# class FpsAccountPayment(http.Controller):
#     @http.route('/fps_account_payment/fps_account_payment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fps_account_payment/fps_account_payment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fps_account_payment.listing', {
#             'root': '/fps_account_payment/fps_account_payment',
#             'objects': http.request.env['fps_account_payment.fps_account_payment'].search([]),
#         })

#     @http.route('/fps_account_payment/fps_account_payment/objects/<model("fps_account_payment.fps_account_payment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fps_account_payment.object', {
#             'object': obj
#         })
