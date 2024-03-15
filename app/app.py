from flask import Flask
from flask import render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

from config import Config
from forms import LoginForm

import fish



app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
db = SQLAlchemy(app)

from models import User


@app.route('/')
@app.route('/index')
def index():
    print(User.query.get(1))
    return render_template('base/base.html')

@app.route('/login/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def auth():
    form = LoginForm()
    error = 'None'
    if form.validate_on_submit():
        error='Не правильный логин или пароль'
    return render_template('login.html', form=form, error=error)


@app.route('/my-tasks/<filter>')
@app.route('/my-tasks/')
@app.route('/my-tasks')
def my_tasks(filter = None):
    buff = fish.tasks
    if filter == 'from-me':
        buff = [buff[0]]
    return render_template('my_tasks.html', tasks = buff, me = fish.me)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

