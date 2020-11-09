import os

from flask import Flask, request
from flask import render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Sequence
from werkzeug.utils import redirect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

project_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql+psycopg2://postgres:123456@127.0.0.1:5432/proyecto'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LeWg_QUAAAAAGWw9pL7XThDWQQgPEMdgzuefZ81"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LeWg_QUAAAAADlz5XrfTWDRrHiDFYRaLhb4oSGM"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, primero inicia sesión'
login_manager.login_message_category='info'

from proyecto import routes