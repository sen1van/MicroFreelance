import os
basedir = os.path.abspath(os.path.dirname(__file__))
basedir = basedir

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    DATA_DIR = basedir
    code_range = [10000,99999]
    code_ttl = 5 # in minutes

