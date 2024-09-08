from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, List
from sqlalchemy import String, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import *
from sqlalchemy.sql import func
from flask_login import UserMixin
import datetime

from app import db
from app import login

class User(UserMixin, db.Model):
    __table_name__ = "users"

    id: Mapped[int]                         = mapped_column(primary_key=True)
    login: Mapped[str]                      = mapped_column(String(64), index=True, unique=True)
    password_hash: Mapped[Optional[str]]    = mapped_column(String(256))
    name: Mapped[Optional[str]]             = mapped_column(String(64))
    aboutme: Mapped[Optional[str]]          = mapped_column(String(256))
    contact_info: Mapped[Optional[str]]     = mapped_column(String(256))
    account_type: Mapped[str]               = mapped_column(String(256), default='student')

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
    create_date: Mapped[datetime.datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime.datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    selected: Mapped[bool]                  = mapped_column(default=False)
    selected_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    archived: Mapped[bool]                  = mapped_column(default=False)
    archived_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    selected_respond_author_id: Mapped[Optional[int]] = mapped_column()

    respond: Mapped[list["PostRespond"]]    = relationship(back_populates="post", cascade="all, delete")
    author: Mapped["User"] = relationship()

class PostRespond(db.Model):
    __table_name__ = "post_responds"

    id: Mapped[int]                         = mapped_column(primary_key=True)
    text: Mapped[str]                       = mapped_column(String(256))
    author_id: Mapped[int]                  = mapped_column(ForeignKey(User.id))
    post_id: Mapped[int]                    = mapped_column(ForeignKey(Post.id))
    selected: Mapped[bool]                  = mapped_column(default=False)
    create_date: Mapped[datetime.datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_date: Mapped[datetime.datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    author: Mapped["User"] = relationship()
    post: Mapped["Post"] = relationship()

class RegCode(db.Model):
    __table_name__ = "reg_code"

    id: Mapped[int]                         = mapped_column(primary_key=True)
    code: Mapped[str]                       = mapped_column(String(256))
    author_id: Mapped[int]                  = mapped_column(ForeignKey(User.id), nullable=False)
    used_id: Mapped[int]                    = mapped_column(ForeignKey(User.id), nullable=True)
    create_date: Mapped[datetime.datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())