from klinik import db, bcrypt

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    password = db.Column(db.Text)
    level = db.Column(db.String(100))
    usernya = db.relationship('Pasien', backref=db.backref('user', lazy=True))

    def __init__(self,username,password,level):
        self.username = username
        if password != '':
            self.password = bcrypt.generate_password_hash(password).decode('UTF-8')
        self.level = level

class Dokter(db.Model):
    __tablename__ = 'dokter'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150))
    jadwal = db.Column(db.Text)

    def __init__(self,nama,jadwal):
        self.nama = nama
        self.jadwal = jadwal

class Suplier(db.Model):
    __tablename__ = 'suplier'
    id = db.Column(db.Integer, primary_key=True)
    perusahaan = db.Column(db.String(200))
    kontak = db.Column(db.String(100))
    alamat = db.Column(db.Text)
    supliernya = db.relationship('Obat', backref=db.backref('suplier', lazy=True))

    def __init__(self,perusahaan,kontak,alamat):
        self.perusahaan = perusahaan
        self.kontak = kontak
        self.alamat = alamat

class Obat(db.Model):
    __tablename__ = 'obat'
    id = db.Column(db.Integer, primary_key=True)
    namaObat = db.Column(db.String(150))
    jenisObat = db.Column(db.String(150))
    harga_beli = db.Column(db.Integer)
    harga_jual = db.Column(db.Integer)
    kondisi = db.Column(db.String(80))
    suplier_id = db.Column(db.Integer, db.ForeignKey('suplier.id'))

    def __init__(self,namaObat,jenisObat,harga_beli,harga_jual,kondisi,suplier_id):
        self.namaObat = namaObat
        self.jenisObat = jenisObat
        self.harga_beli = harga_beli
        self.harga_jual = harga_jual
        self.kondisi = kondisi
        self.suplier_id = suplier_id
        

class Pendaftaran(db.Model):
    __tablename__ = 'pendaftaran'
    id = db.Column(db.BigInteger, primary_key=True)
    nama = db.Column(db.String(150))
    tl = db.Column(db.String(100))
    tg_lahir = db.Column(db.String(100))
    jk = db.Column(db.String(100))
    status = db.Column(db.String(100))
    profesi = db.Column(db.String(100))
    alamat = db.Column(db.Text)
    keterangan = db.Column(db.String(100))
    db.relationship('Pasien', backref=db.backref('pendaftaran', lazy=True))

    def __init__(self,nama,tl,tg_lahir,jk,status,profesi,alamat,keterangan):
        self.nama = nama
        self.tl = tl
        self.tg_lahir = tg_lahir
        self.jk = jk
        self.status = status
        self.profesi = profesi
        self.alamat = alamat
        self.keterangan = keterangan

class Pasien(db.Model):
    __tablename__ = 'pasien'
    id = db.Column(db.BigInteger, primary_key=True)
    nama = db.Column(db.String(150))
    keluhan = db.Column(db.Text)
    diagnosa = db.Column(db.String(100))
    resep = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pendaftaran_id = db.Column(db.BigInteger, db.ForeignKey('pendaftaran.id'))
    tanggal = db.Column(db.String(100))

    def __init__(self,nama,keluhan,diagnosa,resep,user_id,pendaftaran_id,tanggal):
        self.nama = nama
        self.keluhan = keluhan
        self.diagnosa = diagnosa
        self.resep = resep
        self.user_id = user_id
        self.pendaftaran_id = pendaftaran_id
        self.tanggal = tanggal

db.create_all()
