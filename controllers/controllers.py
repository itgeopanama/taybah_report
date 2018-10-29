# -*- coding: utf-8 -*-
from odoo import http

# class Leadreport(http.Controller):
#     @http.route('/taybah_report/taybah_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/taybah_report/taybah_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('taybah_report.listing', {
#             'root': '/taybah_report/taybah_report',
#             'objects': http.request.env['taybah_report.taybah_report'].search([]),
#         })

#     @http.route('/taybah_report/taybah_report/objects/<model("taybah_report.taybah_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('taybah_report.object', {
#             'object': obj
#         })