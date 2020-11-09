from proyecto import db, login_manager
from datetime import datetime
from sqlalchemy import func
from flask_login import UserMixin

@login_manager.user_loader  #Para recordar el Usuario logeado
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin): #"UserMixin", es para facilitar la implementación de una clase de usuario, como: is_authenticated, is_active, is_anonymous, get_id()
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post',backref='author',lazy=True)

    def _repr_(self):
        return f'User({self.username}, {self.email})'
    
class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def _repr_(self):
        return f'Post({self.title}, {self.description})'

class Ploteo(db.Model, UserMixin):
    plo_id=db.Column(db.Integer, primary_key=True)
    plo_fecha_creacion=db.Column(db.DateTime, default=func.now())
    plo_lat=db.Column(db.String(15), nullable=False)
    plo_lon=db.Column(db.String(15), nullable=False)
    plo_fecha=db.Column(db.DateTime, nullable=False)

    def _repr_(self):
        return f'Post({self.plo_lat}, {self.plo_lon})'

class Songs(db.Model, UserMixin):
    son_id=db.Column(db.Integer, primary_key=True)
    son_fecha=db.Column(db.DateTime, default=func.now())
    son_busqueda=db.Column(db.String(60), nullable=False)

    def _repr_(self):
        return f'Post({self.son_fecha}, {self.son_busqueda})'