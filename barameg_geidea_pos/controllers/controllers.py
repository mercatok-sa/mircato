# -*- coding: utf-8 -*-
# from odoo import http


# class BaramegGeideaIntegration(http.Controller):
#     @http.route('/barameg_geidea_pos/barameg_geidea_pos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/barameg_geidea_pos/barameg_geidea_pos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('barameg_geidea_pos.listing', {
#             'root': '/barameg_geidea_pos/barameg_geidea_pos',
#             'objects': http.request.env['barameg_geidea_pos.barameg_geidea_pos'].search([]),
#         })

#     @http.route('/barameg_geidea_pos/barameg_geidea_pos/objects/<model("barameg_geidea_pos.barameg_geidea_pos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('barameg_geidea_pos.object', {
#             'object': obj
#         })
