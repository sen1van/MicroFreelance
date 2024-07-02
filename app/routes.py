from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from sqlalchemy.sql import func
from wand.image import Image
import datetime

import fish
from app import app
from forms import *
from app import db
from models import *
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
            flash(['Не верные логин или пороль', 'red'])
            return redirect(url_for('login'))
        
        flash(['Вы успешно вошли', 'green'])
        login_user(user, remember=True)
        return redirect(url_for('profile'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash(['Вы вышли', 'red'])
    return redirect(url_for('login'))

@app.route('/profile/')
@app.route('/profile')
@app.route('/profile/<login>')
def profile(login = None):
    if login == None and current_user.is_authenticated:
        return redirect(url_for('profile', login = current_user.login))
    is_owner = False
    if current_user.is_authenticated and login == current_user.login:
        is_owner = True
    user = db.session.scalar( sa.select(User).where(User.login == login))
    if user != None:
        return render_template('profile.html', user = user, owner = is_owner)
    return abort(404)
    
@app.route('/profile-editor/', methods=['GET', 'POST'])
@app.route('/profile-editor', methods=['GET', 'POST'])
@login_required
def profile_editor():
    if not current_user.is_authenticated:
        return redirect("/")
    form = ProfileEditorForm()
    print(form.photo, form.errors)
    if form.validate_on_submit():
        user = db.session.scalar( sa.select(User).where(User.id == current_user.id) )
        user.name = form.name.data
        user.aboutme = form.aboutme.data
        db.session.commit()
        print(form.photo.data, 123)
        if form.photo.data:
            with Image(blob=form.photo.data) as img:
                img.format = 'webp'
                img.sample(width=600, height=600)
                img.save(filename=f"{Config.DATA_DIR}/static/avatars/{user.login}.webp")
        flash(['Вы успешно изменили данные', 'green'])
        return redirect(url_for('login'))
    if request.method == 'POST' and not form.validate():
        flash(['Произошла ошибка, возможно ошибка заполнения', 'red'])
    form.aboutme.data = current_user.aboutme
    return render_template('profile_editor.html', user=current_user, form=form)


@app.route('/my-tasks/<filter>')
@app.route('/my-tasks/')
@app.route('/my-tasks')
@login_required
def my_tasks(filter = None):
    return render_template('my_tasks.html', tasks = db.session.query( Post ).filter(Post.author_id == current_user.id).filter(Post.archived == False).order_by(sa.desc(Post.update_date)), create_new = True )

@app.route('/')
@app.route('/index')
@app.route('/all-tasks/<filter>')
@app.route('/all-tasks/')
@app.route('/all-tasks')
def all_tasks(filter = None):
    return render_template('my_tasks.html', tasks = db.session.query( Post ).filter(Post.archived == False).order_by(sa.desc(Post.update_date)), create_new = True)

@app.route('/')
@app.route('/archive/')
@app.route('/archive')
def archive(filter = None):
    return render_template('my_tasks.html', tasks = db.session.query( Post ).filter(Post.archived == True).filter(Post.author_id == current_user.id).order_by(sa.desc(Post.archived)), create_new = False, title='Архив' )

@app.route('/create-post/', methods=['GET', 'POST'])
@app.route('/create-post',  methods=['GET', 'POST'])
@login_required
def create_post():
    if not current_user.is_authenticated:
        return redirect(url_for('my_tasks'))
    form = PostEditorForm()
    if form.validate_on_submit():
        print(form.data_text.data)
        new_post = Post()
        new_post.title = form.title.data
        new_post.data = form.data.data
        new_post.data_text = form.data_text.data
        new_post.coast = form.coast.data
        new_post.currency = form.currency.data
        new_post.author_id = current_user.id
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('my_tasks'))
    data = Post()
    data.author = current_user
    data.title = ''
    data.data = 'Описание'
    data.coast = ''
    data.currency = 'Часов'
    if request.method == 'POST':
        data.title = form.title.data
        data.data = form.data.data
        data.coast = form.coast.data
        data.currency = form.currency.data
        flash(['Произошла ошибка, возможно ошибка заполнения', 'red'])
    data.new_post = True
    return render_template('post.html', edit=True, form=form, current_user=current_user, data = data)

@app.route('/edit-post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    if not current_user.is_authenticated:
        return redirect(url_for('my_tasks'))
    form = PostEditorForm()
    if form.validate_on_submit():
        print(form.data_text.data)
        new_post = db.session.scalar( sa.select(Post).where(Post.id == post_id) )
        new_post.title = form.title.data
        new_post.data = form.data.data
        new_post.data_text = form.data_text.data
        new_post.coast = form.coast.data
        new_post.currency = form.currency.data
        new_post.author_id = current_user.id
        new_post.update_date = func.now()
        db.session.commit()
        flash(['Изменения сохранены', 'green'])
        return redirect(url_for('my_tasks'))
    data = db.session.scalar( sa.select(Post).where(Post.id == post_id) )
    if request.method == 'POST':
        data.title = form.title.data
        data.data = form.data.data
        data.coast = form.coast.data
        data.currency = form.currency.data
        flash(['Произошла ошибка, возможно ошибка заполнения', 'red'])
    return render_template('post.html', edit=True, form=form, current_user=current_user, data = data)

@app.route('/post/<id>', methods=['GET', 'POST'])
def post(id = None):
    data = db.session.scalar( sa.select(Post).where(Post.id == id) )
    if data == None:
        return abort(404)
    if current_user.is_authenticated and current_user.id != data.author_id:
        form = PostRespondForm()
        respond = db.session.query( PostRespond ).filter(PostRespond.author_id == current_user.id).filter(PostRespond.post_id == id).first()
        if form.validate_on_submit():
            if not respond:
                respond = PostRespond()
            respond.text = form.text.data
            respond.author_id = current_user.id
            respond.post_id = id
            respond.update_date = func.now()
            db.session.add(respond)
            db.session.commit()
            flash(['Данные сохранены', 'green'])
        if respond:
            form.text.data = respond.text
            form.submit.label.text = "Изменить"
        responds = respond
    else:
        form=''
        if current_user.is_authenticated and data.author_id == current_user.id:
            responds = data.respond
        else:
            responds = []
    return render_template('post.html', edit=False, form=form, data=data, current_user=current_user, responds=responds)

@app.route('/delete-post/<id>')
@login_required
def delete_post(id = None):
    data = db.session.scalar( sa.select(Post).where(Post.id == id) )
    if data.author_id != current_user.id:
        return abort(418)
    db.session.delete(data)
    db.session.commit()
    flash(['Вы удалили пост', 'green'])
    return redirect(url_for('my_tasks'))

@app.route('/archiving-post/post<post_id>&user<user_id>')
@login_required
def archiving_post(post_id, user_id):
    post = db.session.scalar( sa.select(Post).where(Post.id == post_id) )
    if post.author_id != current_user.id:
        return abort(418)
    post.archived = True
    post.archived_date = func.now()
    respond = db.session.query( PostRespond ).filter(PostRespond.author_id == user_id).filter(PostRespond.post_id == post_id).first()
    respond.selected = True
    db.session.commit()
    return redirect(url_for("post", id=post_id))

@app.route('/chats')
@login_required
def chats():
    return render_template('chats_list.html', current_user = current_user)




@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(401)
def page_not_found(e):
    return render_template('errors/401.html'), 401







@app.route('/create-user-debug/<login>')
def new_user(login):
    u = User()
    u.login = login
    u.set_password('1111')
    db.session.add(u)
    db.session.commit()
    return redirect(url_for("login"))