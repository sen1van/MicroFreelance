from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import *
from flask_login import UserMixin

from app import db
from app import login

class User(UserMixin, db.Model):
    __table_name__ = "Users"

    id: Mapped[int]                         = mapped_column(primary_key=True)
    login: Mapped[str]                      = mapped_column(String(64), index=True, unique=True)
    password_hash: Mapped[Optional[str]]    = mapped_column(String(256))
    name: Mapped[str]                       = mapped_column(String(64))
    aboutme: Mapped[str]                    = mapped_column(String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password) 

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {} : {} : {}>'.format(self.login, self.name, self.id) 
    
@login.user_loader
def load_user(id):
  return db.session.get(User, int(id))