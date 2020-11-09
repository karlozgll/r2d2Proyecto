from flask_wtf import FlaskForm
from datetime import date
from flask_wtf import RecaptchaField
from wtforms.fields import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.fields.html5 import TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
#from wtforms_components import DateRange
from proyecto.models import User
from wtforms_html5 import DateField, DateRange
from proyecto import bcrypt

#FORMS TRABAJAN EN CONJUNTO CON LOS html, Y SON INVOCADOS A PARTIR DE AHÍ , CON SUS RESPECTIVAS VALIDACIONES 

class RegistrationForm(FlaskForm): #FORMAS DE REGISTRO 
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Registrarse")

    def validate_username(self, username): #VALIDACION DE USUARIO EXISTENTE
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso')

    def validate_email(self, email): #VALIDACION DE CONTRASEÑA EXISTENTE
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está en uso')                


class LoginForm(FlaskForm): #FORMAS DE LOGIN
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Iniciar Sesión')
    

class PostForm(FlaskForm): #FORMAS DE PUBLICACION
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    submit = SubmitField('Publicar')

class RecoveryPassForm(FlaskForm): #FORMULARIO DE OLVIDE CONTRASEÑA
    email=StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Recuperar')

    def validate_email(self, email): #VALIDACION DE CONTRASEÑA EXISTENTE
        user=User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Este email no existe') 

class SongForm(FlaskForm): #FORMULARIO DE OLVIDE CONTRASEÑA
    namesong= StringField('Nombre', validators=[DataRequired()],id='namesong')
    submit = SubmitField('Buscar')

class RestablecerForm(FlaskForm): #FORMAS DE REGISTRO 
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Aceptar")

class MapForm(FlaskForm):
    lat = StringField('Latitud', validators=[DataRequired()], id='lat')
    lon = StringField('Longitud', validators=[DataRequired()], id='lon')
    fecha= DateField('Fechita', format='%Y-%m-%d', validators=[DateRange(date(1900,1,1), date(2100,12,31))])
    start = TimeField('Hora')
    submit = SubmitField('Crear')