# -*- coding: utf-8 -*-
from odoo import http

# class PettyCashExtention(http.Controller):
#     @http.route('/petty_cash_extention/petty_cash_extention/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/petty_cash_extention/petty_cash_extention/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('petty_cash_extention.listing', {
#             'root': '/petty_cash_extention/petty_cash_extention',
#             'objects': http.request.env['petty_cash_extention.petty_cash_extention'].search([]),
#         })

#     @http.route('/petty_cash_extention/petty_cash_extention/objects/<model("petty_cash_extention.petty_cash_extention"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('petty_cash_extention.object', {
#             'object': obj
#         })