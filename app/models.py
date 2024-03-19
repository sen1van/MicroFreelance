from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from app import db



class User(db.Model):

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)   

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return '<User {}>'.format(self.username) 
    
# @login.user_loader
# def load_user(id):
#     return db.session.get(User, int(id))


