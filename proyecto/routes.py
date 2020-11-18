from flask import render_template, flash, url_for, redirect, request, abort, jsonify, Response,json, make_response
from proyecto import app, bcrypt, db
from proyecto.forms import RegistrationForm, LoginForm, PostForm, RecoveryPassForm, SongForm, RestablecerForm, MapForm
from proyecto.models import User, Post, Songs, Ploteo
from flask_login import login_user, logout_user, current_user, login_required
from proyecto.clases.recovery import Recovery
from proyecto.clases.spotipy import Spotipy
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from proyecto.clases.astros.stellar import Astros
import proyecto.clases.astros.stellar as astroloco
from flask import send_from_directory
from proyecto.clases.Ipinfo import Ipinfo
from datetime import datetime
import proyecto.clases.pdf as PDFPLO
import os

s = URLSafeTimedSerializer('Thisisasecret!')

@app.route('/about')
def about():
    return render_template('port.html')

# LA RUTA PRINCIPAL HOME O INICIO QUE PRESENTA A TRAVES DEL TEMPLATE index.html LAS PUBLICACIONES REALIZADAS POR EL USUARIO
@app.route('/')
def home():
    
    return render_template('port.html')

@app.route('/comunidad')
def comunidad():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

# RUTA PARA REGISTRAR UN USUARIO, TRABAJA CON EL TEMPLATE "register.html"
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:  # EN EL CASO DE QUE EL USUARIO ESTÉ LOGUEADO Y LA RUTA SE ESCRIBA MANUAL, REDIRECCIONARÁ A LA RUTA PRINCIPAL
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():  # SI EL FORMULARIO SE VALIDA, ENCRIPTA LA CONTRASEÑA, Y GUARDA A "User" EN LA "database.db"
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Cuenta creada para {user.username}', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# RUTA PARA LOGUEAR UN USUARIO, TRABAJA CON EL TEMPLATE "login.html"
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # EN EL CASO DE QUE EL USUARIO ESTÉ LOGUEADO Y LA RUTA SE ESCRIBA MANUAL, REDIRECCIONARÁ A LA RUTA PRINCIPAL
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():  # SI EL FORMULARIO SE VALIDA, BUSCA AL USUARIO CON EL MISMO EMAIL
        user = User.query.filter_by(email=form.email.data).first()
        # SI SU CONTRASEÑA ES VALIDA
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)  # USUARIO LOGUEADO
            flash(f'Bienvenido!, has iniciado sesión con éxito', 'success')
            # EN EL CASO QUE HAYAS IDO DIRECTO A UN LINK DENTRO DE LAS OCPCIONES DE USUARIO TE PEDIRÁ QUE LOGUEES ANTES
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Contraseña incorrecta', 'danger')
    return render_template('login.html', title='Login', form=form)


# RUTA PARA SALIDA DE UN USUARIO LOGUEADO, REDIRECCIONA AL "login.html"
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# RUTA PARA CREAR UNA PUBLICACION DE UN USUARIO, TRABAJA CON EL TEMPLATE "create_post.html"
@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    description=form.description.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash(f'Tu publicación ha sido creada', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Crear Publicación', form=form, heading='Crear Publicación')


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def get_post(post_id):
    post = Post.query.get(post_id)
    return render_template('get_post.html', title=f'Publicación {post_id}', post=post)


# ACTUALIZAR PUBLICACION
@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
def update_post(post_id):
    form = PostForm()
    post = Post.query.get(post_id)
    if current_user != post.author:
        abort(403)
    if form.validate_on_submit():
        post.title = form.title.data
        post.description = form.description.data
        db.session.commit()
        flash('Tu publiacación ha sido actualizada!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.description.data = post.description
    return render_template('create_post.html', title=f'Actualizar Publicación {post_id}', form=form, heading='Actualizar Publicación')


# ELIMINAR PUBLICACION
@app.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if current_user != post.author:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/restablecer', methods=['GET', 'POST'])
def restablecer():
    form = RecoveryPassForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        token = s.dumps(email, salt='email-confirm')
        link = url_for('confirm_email', token=token, _external=True,)
        valores = Recovery(email, user.username, link)
        valores.enviar()
        flash('Se ha enviado el link de restablecimiento de contraseña', 'info')
        return redirect(url_for('login'))
    return render_template('restablecer.html', title='Restablecer', form=form)


@app.route('/songs', methods=['GET', 'POST'])
@login_required
def songs():
    form = SongForm()
    return render_template('songs.html', title='Canciones', form=form)


@app.route('/process', methods=['GET', 'POST'])
def process():
    nombre = request.form['nombre']
    sp = Spotipy()
    resultado = sp.busqueda_cancion(nombre)
    try:
        aux=Songs(son_busqueda=nombre,user_id=current_user.id)
        db.session.add(aux)
        db.session.commit()
    except Exception as e:
        print(e)
    # return resultado
    return render_template('songcard.html', title='Canciones', results=resultado)


@app.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    try:
        if current_user.is_authenticated:  # EN EL CASO DE QUE EL USUARIO ESTÉ LOGUEADO Y LA RUTA SE ESCRIBA MANUAL, REDIRECCIONARÁ A LA RUTA PRINCIPAL
            return redirect(url_for('home'))
        form = RestablecerForm()
        email = s.loads(token, salt='email-confirm', max_age=1800)
        user = User.query.filter_by(email=email).first()
        if form.validate_on_submit():  # SI EL FORMULARIO SE VALIDA, ENCRIPTA LA CONTRASEÑA, Y GUARDA A "User" EN LA "database.db"
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Tu contraseña ha sido actualizada!', 'success')
            return redirect(url_for('login'))
        elif request.method == 'GET':
            form.password.data = user.password
            form.confirm_password.data = user.password
    except SignatureExpired:
        flash('La sesión ha finalizado, intente otra vez', 'danger')
        return redirect(url_for('login'))
    return render_template('confirm_email.html', title='Restablecer Contraseña', form=form)

@app.route('/maps', methods=['GET', 'POST'])
@login_required
def maps():

    form = MapForm()
    return render_template('maps.html', title='Mapa', form=form)


@app.route('/ploteomaps', methods=['GET', 'POST'])
def ploteomaps():
    form = MapForm(request.form)
    lat = form.lat.data
    lon = form.lon.data
    fecha = form.fecha.data
    hora=form.start.data
    fecha_hora=datetime.combine(fecha,hora)
    astroloco.funcion_principal(lat, lon, fecha_hora)
    resultado = 'astros' + lat + "_" + \
        fecha_hora.strftime("%Y-%m-%d-%H-%M-%S")+'.svg'
    try:
        aux=Ploteo(plo_lat=lat, plo_lon=lon, plo_fecha=datetime.combine(fecha,hora),user_id=current_user.id)
        db.session.add(aux)
        db.session.commit()
    except Exception as e:
        print("ERROR: ",e)
    return render_template('ploteo.html', title='Mapa', results=resultado)

@app.route('/getIP', methods=['GET', 'POST'])
def getIP():
    if request.method == 'POST':
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip = (request.environ['REMOTE_ADDR'])
        else:
            ip = (request.environ['HTTP_X_FORWARDED_FOR'])
    else:
        ip = request.args.get('ip')
    IP = Ipinfo()
    data = IP.ip_scraping(ip)
    return data

@app.route('/reporte-ploteos', methods=['GET', 'POST'])
@login_required
def reporteploteo():
    reg=db.session.query(Ploteo).filter_by(user_id=current_user.id).all()
    return render_template('reporte-ploteo.html',registros=reg)

@app.route('/reporte-cancion', methods=['GET', 'POST'])
@login_required
def reportecancion():
    reg=db.session.query(Songs).filter_by(user_id=current_user.id).all()
    return render_template('reporte-cancion.html',registros=reg)    

@app.route('/reportar-ploteos', methods=['GET', 'POST'])
@login_required
def reportarploteos():
    plts = db.session.query(Ploteo).filter_by(user_id=current_user.id).all()
    respuesta = PDFPLO.pdfPloteo(plts)
    return respuesta

@app.route('/reportar-canciones', methods=['GET', 'POST'])
@login_required
def reportarcanciones():
    plts = db.session.query(Songs).filter_by(user_id=current_user.id).all()
    respuesta = PDFPLO.pdfPloteo2(plts)
    return respuesta
