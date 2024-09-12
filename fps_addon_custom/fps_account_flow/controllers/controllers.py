# -*- coding: utf-8 -*-
# from odoo import http


# class FpsAccountFlow(http.Controller):
#     @http.route('/fps_account_flow/fps_account_flow', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fps_account_flow/fps_account_flow/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fps_account_flow.listing', {
#             'root': '/fps_account_flow/fps_account_flow',
#             'objects': http.request.env['fps_account_flow.fps_account_flow'].search([]),
#         })

#     @http.route('/fps_account_flow/fps_account_flow/objects/<model("fps_account_flow.fps_account_flow"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fps_account_flow.object', {
#             'object': obj
#         })
