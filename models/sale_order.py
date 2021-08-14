from typing import BinaryIO, ChainMap
from odoo import api, fields, models


class sale_order(models.Model):
    _inherit = 'sale.order'

    paket_perjalanan_id = fields.Many2one(
        comodel_name='paket.perjalanan',
        string='Paket Perjalanan',
        domain=[('state', '=', 'confirm')],
    )

    dokumen_line = fields.One2many(
        comodel_name='sale.dokumen.line',
        inverse_name='order_id',
        string='Dokumen Lines',
    )
    passport_line = fields.One2many(
        comodel_name='sale.passport.line',
        inverse_name='order_id',
        string='Passport Lines',
    )

    @api.onchange('paket_perjalanan_id')
    def set_order_line(self):
        res = {}
        if self.paket_perjalanan_id:
            pp = self.paket_perjalanan_id
### Otomatis - Nilai di set otomatis dari method onchange product_id_change() ###
            order = self.env['sale.order'].new({
                'partner_id': self.partner_id.id,
                'pricelist_id': self.pricelist_id.id,
                'date_order': self.date_order
            })

            line = self.env['sale.order.line'].new({
                'product_id':pp.product_id.id,
                'order_id':order.id
            })
            line.product_id_change()

            vals = line._convert_to_write({
                name: line[name]for name in line._cache
            })
            self.order_line = line
            return res


class sale_dokumen_line(models.Model):
    _name = 'sale.dokumen.line'
    
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sales Order',
        ondelete='cascade',
    )
    name = fields.Char(string='Name', required=True, )
    foto = fields.Binary(string='Photo', required=True, )


class sale_passport_line(models.Model):
    _name = 'sale.passport.line'
    
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sales Orders',
        ondelete='cascade'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Jamaah',
        required=True, 
    )
    name = fields.Char(string='Name in Passport', required=True, )
    nomor = fields.Char(string='Passport Number', required=True, )
    masa_berlaku = fields.Date(string='Date of Expiry', required=True, )
    tipe_kamar = fields.Selection([('d', 'Double'), ('t', 'Triple'), ('q', 'Quad')], string='Room type', required=True, )
    foto = fields.Binary(string='Photo',required=True, )



    
