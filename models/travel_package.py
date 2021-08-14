
import base64
import xlsxwriter
from odoo import _
from odoo import api, fields, models
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO

class paket_perjalanan(models.Model):
    _name = 'paket.perjalanan'
    _description = "Paket Perjalanan"

    name = fields.Char(string='Reference',readonly=True, default='/')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,    
    )
    tanggal_berangkat = fields.Date(string='Tanggal Berangkat')
    tanggal_pulang = fields.Date(string='Tanggal Pulang')
    quota = fields.Integer(string='Quota')
    quota_progress = fields.Float(string='Quota Progress',compute='_taken_seats',)
    note = fields.Text(string='Notes')
    hotel_line = fields.One2many(
        comodel_name='paket.hotel.line',
        inverse_name='paket_perjalanan_id',
        string='Hotels Lines',
    )
    pesawat_line = fields.One2many(
        comodel_name='paket.pesawat.line',
        inverse_name='paket_perjalanan_id',
        string='Air Lines',
    )
    acara_line = fields.One2many(
        comodel_name='paket.acara.line',
        inverse_name='paket_perjalanan_id',
        string='Schedule Line',
    )
    peserta_line = fields.One2many(
        comodel_name='paket.peserta.line',
        inverse_name='paket_perjalanan_id',
        string='Jamaah Lines',
        readonly=True,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ], string=' ', readonly=True, copy=False, default='draft', track_visibility='onchange')

    date_created = fields.Date(string='Date Created', default=fields.Date.today())
    title = fields.Char(string='judul', default="Jamaah Lines")
    data_file = fields.Binary(string='Data Jamaah lines')
    filename = fields.Char(string='Filename')



    def action_confirm(self):
        self.write({'state': 'confirm'})
        

    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('paket.perjalanan')
        return super(paket_perjalanan,self).create(vals)

    def name_get(self):
        return [(this.id,this.name + "#" + " "+ this.product_id.partner_ref) for this in self]

    @api.depends('quota','peserta_line')
    def _taken_seats(self):
        for r in self:
            if not r.quota:
                r.quota_progress = 0.0
            else:
                r.quota_progress = 100.0 * len(r.peserta_line) / r.quota
    
    def update_jamaah(self):
        order_ids = self.env['sale.order'].search([('paket_perjalanan_id', '=', self.id), ('state', 'not in', ('draft', 'cancel'))])
        if order_ids:
            self.peserta_line.unlink()
            for o in order_ids:
                for x in o.passport_line:
                    self.peserta_line.create({
                        'paket_perjalanan_id': self.id,
                        'partner_id': x.partner_id.id,
                        'name': x.name,
                        'order_id': o.id,
                        'jenis_kelamin': x.partner_id.jenis_kelamin,
                        'tipe_kamar': x.tipe_kamar,
                    })

    def export(self):
        # Membuat Worksheet
        folder_title = "Jamaah lines" + "-" + str(self.date_created) + ".xlsx"
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        ws = workbook.add_worksheet(("Jamaah Lines"))  

        # Menambahkan style
        style = workbook.add_format({'left': 1, 'top': 1,'right':1,'bold': True,'fg_color': '#339966','font_color': 'white','align':'center'})
        style.set_text_wrap()
        style.set_align('vcenter')
        style_bold = workbook.add_format({'left': 1, 'top': 1,'right':1,'bottom':1,'bold': True,'align':'center','num_format':'_(Rp* #,##0_);_(Rp* (#,##0);_(* "-"??_);_(@_)'})
        style_bold_orange = workbook.add_format({'left': 1, 'top': 1,'right':1,'bold': True,'align':'center','fg_color': '#FF6600','font_color': 'white'})
        style_no_bold = workbook.add_format({'left': 1,'right':1,'bottom':1, })
        style_date = workbook.add_format({'left': 1, 'top': 1,'right':1,'bold': False,'align':'left','num_format': 'dd/mm/yy'})

        # Membuat Column Header Jamaah Lines
        ws.merge_range('A1:D1',  self.title + ' ' + str(self.date_created), style_bold)
        ws.set_column(1, 1, 10)
        ws.set_column(1, 2, 40)
        ws.set_column(1, 3, 25)
        ws.set_column(1, 4, 25)
        ws.set_column(1, 5, 25)
        ws.set_column(1, 6, 25)
        ws.set_column(1, 7, 25)
        ws.set_column(1, 8, 25)
        ws.set_column(1, 9, 25)
        ws.set_column(1, 10, 25)
        ws.set_column(1, 11, 25)
        ws.set_column(1, 12, 25)
        ws.set_column(1, 13, 25)
        ws.set_column(1, 14, 25)

        ws.write(3, 0,'NO ', style_bold_orange)
        ws.write(3, 1, 'GENDER', style_bold_orange)
        ws.write(3, 2, 'GENDER', style_bold_orange)
        ws.write(3, 3, 'NAMA ', style_bold_orange)
        ws.write(3, 4, 'TEMPAT LAHIR ', style_bold_orange)
        ws.write(3, 5, 'TANGGAL LAHIR ', style_bold_orange)
        ws.write(3, 6, 'NO PASSPORT ', style_bold_orange)
        ws.write(3, 7, 'PASSPORT ISSUED', style_bold_orange)
        ws.write(3, 8, 'PASSPORT EXPIRED', style_bold_orange)
        ws.write(3, 9, 'IMIGRASI', style_bold_orange)
        ws.write(3, 10, 'MAHRAM', style_bold_orange)
        ws.write(3, 11, 'USIA', style_bold_orange)
        ws.write(3, 12, 'NIK', style_bold_orange)
        ws.write(3, 13, 'ORDER', style_bold_orange)
        ws.write(3, 14, 'ROOM TYPE', style_bold_orange)
        ws.write(3, 15, 'ALAMAT', style_bold_orange)

        row_count = 4
        count = 1

        # Mengisi data pada setiap baris & kolom Jamaah Lines
        for peserta in self.peserta_line.partner_id:
            ws.write(row_count, 0, str(count), style_no_bold)
            if peserta.jenis_kelamin == "pria":
                title = "Mister"
            else:
                title = "Madam"
            ws.write(row_count, 1,title, style_no_bold)
            ws.write(row_count, 2,peserta.jenis_kelamin, style_no_bold)
            ws.write(row_count, 3,peserta.name, style_no_bold)
            ws.write(row_count, 4,peserta.tempat_lahir, style_no_bold)
            ws.write(row_count, 5,str(peserta.tanggal_lahir), style_no_bold)

            #filter nomor passport
            passport_id = []
            passport_id = self.env['sale.passport.line'].search([('order_id.paket_perjalanan_id', '=',self.id),('partner_id.id','=',peserta.id),])

            ws.write(row_count, 6,passport_id.nomor, style_no_bold)
            ws.write(row_count, 7,passport_id.order_id.date_order, style_date)
            ws.write(row_count, 8,passport_id.masa_berlaku, style_date)
            ws.write(row_count, 9,peserta.city, style_no_bold)
            ws.write(row_count, 10,peserta.mahram.name, style_no_bold)
            ws.write(row_count, 11,peserta.age, style_no_bold)
            ws.write(row_count, 12,peserta.no_identitas, style_no_bold)
            ws.write(row_count, 13,passport_id.order_id.name, style_no_bold)

            if passport_id.tipe_kamar == 'd':
                tipe_kamar = 'Double'
            elif passport_id.tipe_kamar == 't':
                tipe_kamar = 'Triple'
            else:
                tipe_kamar = 'Quadruple'
            ws.write(row_count, 14,tipe_kamar, style_no_bold)
            ws.write(row_count, 15,peserta.street, style_no_bold)
            # ws.write(row_count, 14,peserta.street, style_no_bold)
            count+=1
            row_count+=1
        
        row_count+=2
        count = 1

        # Membuat Header untuk Airlines
        ws.write(row_count, 2, 'NO ', style_bold_orange)
        ws.write(row_count, 3, 'AIRLINES ', style_bold_orange)
        ws.write(row_count, 4, 'DEPARTURE DATE ', style_bold_orange)
        ws.write(row_count, 5, 'DEPARTURE CITY ', style_bold_orange)
        ws.write(row_count, 6, 'ARRIVAL CITY ', style_bold_orange)
        
        # Mengisi data pada setiap baris & kolom Air Lines
        for airline in self.pesawat_line:
            row_count+=1
            ws.write(row_count, 2, str(count), style_no_bold)
            ws.write(row_count, 3,airline.partner_id.name, style_no_bold)
            ws.write(row_count, 4,airline.tanggal_berangkat, style_date)
            ws.write(row_count, 5,airline.kota_asal, style_no_bold)
            ws.write(row_count, 6,airline.kota_tujuan, style_no_bold)
            count+=1
        
        # Menyimpan data di field data_file
        workbook.close()        
        out = base64.encodestring(file_data.getvalue())
        self.write({'data_file': out, 'filename': folder_title})

        return self.view_form()

    def view_form(self):        
        view = self.env.ref('travel_umrah.paket_perjalanan_view_form')
        return {
            'name':_('Paket Perjalanan'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'paket.perjalanan',
            'views': [(view.id, 'form')],
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }    

class paket_hotel_line(models.Model):
    _name = 'paket.hotel.line'
    
    paket_perjalanan_id = fields.Many2one('paket.perjalanan', string='Paket Perjalanan',ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Hotel', required=True)
    tanggal_awal = fields.Date(string='Tanggal Mulai', required=True)
    tanggal_akhir = fields.Date(string='Tanggal Berakhir', required=True, )
    kota = fields.Char(
        string="Kota",
        related="partner_id.city",
        readonly=True,
    )

class paket_pesawat_line(models.Model):
    _name = 'paket.pesawat.line'

    paket_perjalanan_id = fields.Many2one('paket.perjalanan', string='Paket Perjalanan', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Airlines', required=True)
    tanggal_berangkat = fields.Date(string='Tanggal Keberangkatan', required=True)
    kota_asal = fields.Char(string='Kota Keberangkatan', required=True)
    kota_tujuan = fields.Char(string='Kota Kedatangan', required=True)


class paket_acara_line(models.Model):
    _name = 'paket.acara.line'  
    
    paket_perjalanan_id = fields.Many2one('paket.perjalanan', string='Paket Perjalanan', ondelete='cascade')
    name = fields.Char(string='Nama Acara', required=True)
    tanggal = fields.Date(string='Tanggal', required=True)


class paket_peserta_line(models.Model):
    _name = 'paket.peserta.line'

    paket_perjalanan_id = fields.Many2one('paket.perjalanan', string='Paket Perjalanan', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Jamaah',)
    name = fields.Char(string='Name in Passport')
    order_id = fields.Many2one('sale.order', string='Sales Orders')
    jenis_kelamin = fields.Selection([('pria', 'Man'), ('wanita', 'Woman')], string='Gender')
    tipe_kamar = fields.Selection([('d', 'Double'), ('t', 'Triple'), ('q', 'Quad')], string='Room Type')

    

    