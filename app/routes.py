from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from forms import LoginForm
from models import User
import fish


@app.route('/')
@app.route('/index')
def index():
    return render_template('base/base.html')

@app.route('/login/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    error = 'None'
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data)
        if user is None or not user.check_password(form.password.data):
            error='Не правильный логин или пароль'
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', form=form, error=error)


@app.route('/my-tasks/<filter>')
@app.route('/my-tasks/')
@app.route('/my-tasks')
def my_tasks(filter = None):
    buff = fish.tasks
    if filter == 'from-me':
        buff = [buff[0]]
    return render_template('my_tasks.html', tasks = buff, me = fish.me)
