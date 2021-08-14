from odoo import api, fields, models
from datetime import date

class ResPartner(models.Model):
    _inherit = 'res.partner'


    no_identitas = fields.Char(string='No KTP')
    jenis_kelamin = fields.Selection([
        ("pria","Pria"),
        ("wanita","Wanita")
        ], string='Jenis Kelamin')

    nama_ayah = fields.Char(string='Nama Ayah')
    nama_ibu = fields.Char(string='Nama Ibu')
    pekerjaan = fields.Char(string='Pekerjaan')
    tempat_lahir = fields.Char(string='Tempat Lahir')
    tanggal_lahir = fields.Date(string='Tanggal Lahir')
    gol_darah = fields.Selection([
        ("a","A"),
        ("b","B"),
        ("ab","AB"),
        ("o","O")], string='Golongan Darah')    

    status_nikah = fields.Selection([
        ("kawin","Kawin"),
        ("notKawin","Belum Kawin")], string='Status Menikah')

    pendidikan = fields.Selection([
        ("sd","SD"),
        ("smp","SMP"),
        ("sma","SMA"),
        ("d3","D3"),
        ("s1","S1"),
        ("s2","S2"),
        ("s3","S3"),
        ("tidak_sekolah","Tidak Sekolah")], string='Pendidikan')

    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        readonly=True,
        store=False,
        compute_sudo = True,
    )

    mahram = fields.Many2one(
        comodel_name='res.partner',
        string='Mahram',
        domain=[("status_nikah", "=", "kawin")],
    )

    @api.depends('tanggal_lahir')
    def _compute_age(self):
        for o in self:
            o.age = False
            if o.tanggal_lahir == date.today():
                o.age = 0
            elif o.tanggal_lahir:
                delta = date.today() - o.tanggal_lahir
                o.age = delta.days / 365

    @api.constrains('tanggal_lahir')
    def check_tanggal_lahir(self):
        if self.tanggal_lahir> date.today():
            raise models.ValidationError("Tanggal lahir harus berasal dari masalalu")
