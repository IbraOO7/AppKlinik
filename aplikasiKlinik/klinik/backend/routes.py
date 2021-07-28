from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, current_app, make_response
from sqlalchemy import func, or_
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired
from flask_bootstrap import Bootstrap
from functools import wraps
from flask_migrate import Migrate
import datetime
import pdfkit
from klinik import app, db, bcrypt, bootstrap, migrate
from .models import *

class Login(FlaskForm):
    username = StringField('', validators=[InputRequired()], render_kw={'autofocus':True, 'placeholder':'Username'})
    password = PasswordField('', validators=[InputRequired()], render_kw={'autofocus':True, 'placeholder':'Password'})
    level = SelectField('', validators=[InputRequired()], choices=[('Admin','Admin'), ('Dokter','Dokter'),
                                                                   ('Administrasi','Administrasi')])

def login_dulu(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'login' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def index():
    if session.get('login') == True:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('login') == True:
        return redirect(url_for('dashboard'))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data) and user.level == form.level.data:
                session['login'] = True
                session['id'] = user.id
                session['level'] = user.level
                session['user'] = user.username
                return redirect(url_for('dashboard'))
        pesan = "Username atau Password anda salah"
        return render_template("login.html", pesan=pesan, form=form)
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_dulu
def dashboard():
    data1 = db.session.query(Dokter).count()
    data2 = db.session.query(Pendaftaran).count()
    data3 = db.session.query(User).count()
    data4 = db.session.query(func.sum(Obat.harga_jual)).filter(Obat.kondisi == "Rusak").scalar()
    data5 = db.session.query(func.sum(Obat.harga_jual)).filter(Obat.kondisi == "Baik").scalar()
    return render_template('dashboard.html',data1=data1,data2=data2,data3=data3,data4=data4,data5=data5)

@app.route('/kelola_user')
@login_dulu
def kelola_user():
    data = User.query.all()
    return render_template('user.html', data=data)

@app.route('/tambahuser', methods=['GET','POST'])
@login_dulu
def tambahuser():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        level = request.form['level']
        db.session.add(User(username,password,level))
        db.session.commit()
        return redirect(url_for('kelola_user'))

@app.route('/edituser/<id>', methods=['GET','POST'])
@login_dulu
def edituser(id):
    data = User.query.filter_by(id=id).first()
    if request.method == "POST":
        try:
            data.username = request.form['username']
            if data.password != '':
                data.password = bcrypt.generate_password_hash(request.form['password']).decode('UTF-8')
            data.level = request.form['level']
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('kelola_user'))
        except:
            flash("Ada trouble")
            return redirect(request.referrer)

@app.route('/hapususer/<id>', methods=['GET','POST'])
@login_dulu
def hapususer(id):
    data = User.query.filter_by(id=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('kelola_user'))

@app.route('/pendaftaran')
@login_dulu
def pendaftaran():
    data = Pendaftaran.query.all()
    return render_template('pendaftaran.html', data=data)

@app.route('/tambahdaftar', methods=['GET','POST'])
@login_dulu
def tambahdaftar():
    if request.method == "POST":
        nama = request.form['nama']
        tl = request.form['tl']
        tg_lahir = request.form['tg_lahir']
        jk = request.form['jk']
        status = request.form['status']
        profesi = request.form['profesi']
        alamat = request.form['alamat']
        keterangan = request.form['keterangan']
        db.session.add(Pendaftaran(nama,tl,tg_lahir,jk,status,profesi,alamat,keterangan))
        db.session.commit()
        return jsonify({'success':True})
        

@app.route('/apotik')
@login_dulu
def apotik():
    data = Obat.query.all()
    data1 = Suplier.query.all()
    return render_template('apotik.html', data=data,data1=data1)

@app.route('/tambahobat', methods=['GET','POST'])
@login_dulu
def tambahobat():
    if request.method == "POST":
        namaObat = request.form['namaObat']
        jenisObat = request.form['jenisObat']
        harga_beli = request.form['harga_beli']
        harga_jual = request.form['harga_jual']
        kondisi = request.form['kondisi']
        suplier_id = request.form['suplier_id']
        db.session.add(Obat(namaObat,jenisObat,harga_beli,harga_jual,kondisi,suplier_id))
        db.session.commit()
        return jsonify({'success':True})

@app.route('/editobat/<id>', methods=['GET','POST'])
@login_dulu
def editobat(id):
    data = Obat.query.filter_by(id=id).first()
    if request.method == "POST":
        data.namaObat = request.form['namaObat']
        data.jenisObat = request.form['jenisObat']
        data.harga_beli = request.form['harga_beli']
        data.harga_jual = request.form['harga_jual']
        data.kondisi = request.form['kondisi']
        data.suplier_id = request.form['suplier_id']
        db.session.add(data)
        db.session.commit()
        return jsonify({'success':True})

@app.route('/dokter')
@login_dulu
def dokter():
    data = Dokter.query.all()
    return render_template('dokter.html', data=data)

@app.route('/tambahdokter', methods=['GET','POST'])
@login_dulu
def tambahdokter():
    if request.method == 'POST':
        nama = request.form['nama']
        jadwal = request.form['jadwal']
        db.session.add(Dokter(nama,jadwal))
        db.session.commit()
        return jsonify({'success':True})
    else:
        return redirect(request.referrer)

@app.route('/editdokter/<id>', methods=['GET','POST'])
@login_dulu
def editdokter(id):
    data = Dokter.query.filter_by(id=id).first()
    if request.method == 'POST':
        data.nama = request.form['nama']
        data.jadwal = request.form['jadwal']
        db.session.add(data)
        db.session.commit()
        return jsonify({'success':True})
    else:
        return redirect(request.referrer)

@app.route('/hapusdokter/<id>', methods=['GET','POST'])
@login_dulu
def hapusdokter(id):
    data = Dokter.query.filter_by(id=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(request.referrer)
        
@app.route('/suplier')
@login_dulu
def suplier():
    data = Suplier.query.all()
    return render_template('suplier.html', data=data)

@app.route('/tambahsuplier', methods=['GET','POST'])
@login_dulu
def tambahsuplier():
    if request.method == "POST":
        perusahaan = request.form['perusahaan']
        kontak = request.form['kontak']
        alamat = request.form['alamat']
        db.session.add(Suplier(perusahaan,kontak,alamat))
        db.session.commit()
        return jsonify({'success':True})

@app.route('/editsuplier/<id>', methods=['GET','POST'])
@login_dulu
def editsuplier(id):
    data = Suplier.query.filter_by(id=id).first()
    if request.method == "POST":
        data.perusahaan = request.form['perusahaan']
        data.kontak = request.form['kontak']
        data.alamat = request.form['alamat']
        db.session.add(data)
        db.session.commit()
        return jsonify({'success':True})

@app.route('/hapusSuplier', methods=['GET','POST'])
@login_dulu
def hapusSuplier(id):
    data = Suplier.query.filter_by(id=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/tangani_pasien')
@login_dulu
def tangani_pasien():
    data = Pendaftaran.query.filter_by(keterangan="Diproses").all()
    return render_template('tangani.html',data=data)

@app.route('/diagnosis/<id>', methods=['GET','POST'])
@login_dulu
def diagnosis(id):
    data = Pendaftaran.query.filter_by(id=id).first()
    if request.method == "POST":
        nama = request.form['nama']
        keluhan = request.form['keluhan']
        diagnosa = request.form['diagnosa']
        resep = request.form['resep']
        user_id = request.form['user_id']
        pendaftaran_id = request.form['pendaftaran_id']
        tanggal = datetime.datetime.now().strftime("%d %B %Y Jam %H:%M:%S")
        data.keterangan = "Selesai"
        db.session.add(data)
        db.session.commit()
        db.session.add(Pasien(nama,keluhan,diagnosa,resep,user_id,pendaftaran_id,tanggal))
        db.session.commit()
        return redirect(request.referrer)

@app.route('/pencarian')
@login_dulu
def pencarian():
    return render_template('pencarian.html')

@app.route('/cari_data', methods=['GET','POST'])
@login_dulu
def cari_data():
    if request.method == 'POST':
        keyword = request.form['q']
        formt = "%{0}%".format(keyword)
        datanya = Pasien.query.join(User, Pasien.user_id == User.id).filter(or_(Pasien.tanggal.like(formt))).all()
        if datanya:
            flash("Data berhasil di temukan")
            tombol = "tombol"
        elif not datanya:
            pesan = "Data tidak berhasil di temukan"
            return render_template('pencarian.html',datanya=datanya,pesan=pesan)
        return render_template('pencarian.html',datanya=datanya,tombol=tombol,keyword=keyword)

@app.route('/cetak_pdf/<keyword>', methods=['GET','POST'])
@login_dulu
def cetak_pdf(keyword):
    formt = "%{0}%".format(keyword)
    datanya = Pasien.query.join(User, Pasien.user_id == User.id).filter(or_(Pasien.tanggal.like(formt))).all()
    html = render_template("pdf.html",datanya=datanya)
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(html, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=laporan.pdf'
    return response

@app.route('/logout')
@login_dulu
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
