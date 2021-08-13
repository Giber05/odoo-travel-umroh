# -*- coding: utf-8 -*-
# from odoo import http


# class TravelUmrah(http.Controller):
#     @http.route('/travel_umrah/travel_umrah/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/travel_umrah/travel_umrah/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('travel_umrah.listing', {
#             'root': '/travel_umrah/travel_umrah',
#             'objects': http.request.env['travel_umrah.travel_umrah'].search([]),
#         })

#     @http.route('/travel_umrah/travel_umrah/objects/<model("travel_umrah.travel_umrah"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('travel_umrah.object', {
#             'object': obj
#         })
