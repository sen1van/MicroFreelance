from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, List
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import *
from flask_login import UserMixin

from app import db
from app import login

class User(UserMixin, db.Model):
    __table_name__ = "users"

    id: Mapped[int]                         = mapped_column(primary_key=True)
    login: Mapped[str]                      = mapped_column(String(64), index=True, unique=True)
    password_hash: Mapped[Optional[str]]    = mapped_column(String(256))
    name: Mapped[Optional[str]]             = mapped_column(String(64))
    aboutme: Mapped[Optional[str]]          = mapped_column(String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password) 

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {} : {} : {}>'.format(self.login, self.name, self.id) 
    
@login.user_loader
def load_user(id):
  return db.session.get(User, int(id))

class Post(db.Model):
    __table_name__ = "posts"

    id: Mapped[int]                         = mapped_column(primary_key=True)
    title: Mapped[str]                      = mapped_column(String(64))
    data: Mapped[str]                       = mapped_column(String(256))
    data_text: Mapped[str]                  = mapped_column(String(256))
    coast: Mapped[str]                      = mapped_column(String(64))
    currency: Mapped[str]                   = mapped_column(String(64))
    author_id: Mapped[int]                  = mapped_column(ForeignKey(User.id))
    create_date: Mapped[str]                = mapped_column(String(64))
    update_date: Mapped[str]                = mapped_column(String(64))

    author: Mapped["User"] = relationship()