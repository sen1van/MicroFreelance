from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
import sqlalchemy as sa
from wand.image import Image

import fish
from app import app
from forms import LoginForm, ProfileEditorForm
from app import db
from models import User
from config import Config

@app.route('/login/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile', login = current_user.login))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar( sa.select(User).where(User.login == form.login.data) )
        if user is None or not user.check_password( form.password.data ):
            flash('Не верные логин или пороль')
            return redirect(url_for('login'))
        
        flash('Вы успешно вошли')
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/')
@app.route('/index')
@app.route('/my-tasks/<filter>')
@app.route('/my-tasks/')
@app.route('/my-tasks')
def my_tasks(filter = None):
    buff = fish.tasks
    if filter == 'from-me':
        buff = [buff[0]]
    return render_template('my_tasks.html', tasks = buff, me = fish.me)

@app.route('/profile/')
@app.route('/profile')
@app.route('/profile/<login>')
def profile(login = None):
    if login == None and current_user.is_authenticated:
        return redirect(url_for('profile', login = current_user.login))
    is_owner = False
    if current_user.is_authenticated and login == current_user.login:
        is_owner = True
    return render_template('profile.html', user = db.session.scalar( sa.select(User).where(User.login == login)), owner = is_owner)
    
@app.route('/profile-editor/', methods=['GET', 'POST'])
@app.route('/profile-editor', methods=['GET', 'POST'])
def profile_editor():
    if not current_user.is_authenticated:
        return redirect(url_for('my_tasks'))
    form = ProfileEditorForm()
    print(form.photo, form.errors)
    if form.validate_on_submit():
        user = db.session.scalar( sa.select(User).where(User.id == current_user.id) )
        print(user)
        user.name = form.name.data
        user.aboutme = form.aboutme.data
        db.session.commit()
        print(form.photo.data, 123)
        if form.photo.data:
            with Image(blob=form.photo.data) as img:
                img.format = 'webp'
                img.sample(width=600, height=600)
                img.save(filename=f"{Config.DATA_DIR}/static/avatars/{user.login}.webp")
        return redirect(url_for('login'))
    form.aboutme.data = current_user.aboutme
    return render_template('profile_editor.html', user=current_user, form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('my_tasks'))
