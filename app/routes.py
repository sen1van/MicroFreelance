from flask import render_template, flash, redirect, url_for, request, abort, jsonify
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from sqlalchemy.sql import func
from wand.image import Image
import datetime
import random

from app import app
from forms import LoginForm, RegisterForm, ProfileEditorForm, PostEditorForm
from forms import AdminUserEditForm, PostRespondForm
from app import db
from models import User, Post, PostRespond, Notification, RegCode
from config import Config


# idk how do it better
# TODO: find the right way to do this
base_render_teplate = render_template
def render_template(*args, **kwargs):
    kwargs['current_user'] = current_user
    return base_render_teplate(*args, **kwargs)


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

@app.route('/register/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile', login = current_user.login))
    form = RegisterForm()

    if form.validate_on_submit():
        code = db.session.scalar( sa.select(RegCode).where(RegCode.code == form.code.data) )
        if code is None:
            flash(['Код не найден', 'red'])
            return redirect(url_for('register'))
        if code.create_date < datetime.datetime.utcnow() - datetime.timedelta(minutes=Config.code_ttl):
            flash(['Код устарел', 'red'])
            return redirect(url_for('register'))
        if code.used_id is not None:
            flash(['Код уже используется', 'red'])
            return redirect(url_for('register'))
        if db.session.scalar( sa.select(User).where(User.login == form.login.data) ) is not None:
            flash(['Логин уже используется', 'red'])
            return redirect(url_for('register'))
        user = User()
        user.name = form.name.data
        user.login = form.login.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        code.used_id = user.id
        db.session.commit()
        flash(['Вы зарегестрировались', 'green'])
        login_user(user, remember=True)
        return redirect(url_for('profile'))
    return render_template('register.html', form=form)


@app.route('/reg-code', methods=['GET', 'POST'])
@login_required
def reg_code():
    if not current_user.is_authenticated:
        return abort(401)
    if not current_user.check_role(['admin', 'teacher']):
        return abort(418)
    code = db.session.scalar( sa.select(RegCode)
        .where(RegCode.author_id == current_user.id)
        .where(RegCode.create_date > datetime.datetime.utcnow() - datetime.timedelta(minutes=Config.code_ttl))
        .where(RegCode.used_id is None))
    if code is None:
        code = RegCode()
        try_code = random.randint(*Config.code_range)
        while db.session.scalar(sa.select(RegCode).where(RegCode.code == try_code)) is not None:
            try_code = random.randint(*Config.code_range)
        code.code = try_code
        code.author_id = current_user.id
        db.session.add(code)
        db.session.commit()
    return render_template('reg-code.html', code=code.code)


@app.route('/logout')
def logout():
    logout_user()
    flash(['Вы вышли', 'red'])
    return redirect(url_for('login'))

@app.route('/profile/')
@app.route('/profile')
@app.route('/profile/<login>')
def profile(login = None):
    if login is None and current_user.is_authenticated:
        return redirect(url_for('profile', login = current_user.login))
    is_owner = False
    if current_user.is_authenticated and login == current_user.login:
        is_owner = True
    user = db.session.scalar( sa.select(User).where(User.login == login))
    if user is not None:
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
        user.contact_info = form.contact_info.data
        print(form.contact_info.data)
        db.session.commit()
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
    form.contact_info.data = current_user.contact_info
    return render_template('profile_editor.html', form=form)


@app.route('/my-tasks/<filter>')
@app.route('/my-tasks/')
@app.route('/my-tasks')
@login_required
def my_tasks(filter = None):
    if current_user.check_role(['admin', 'teacher']):
        query = sa.select(Post)                         \
            .where(Post.author_id == current_user.id)   \
            .where(Post.archived == False)              \
            .order_by(Post.selected.desc(), Post.update_date.desc())
    else:
        query = sa.select(Post)                         \
            .where(Post.archived == False)                                    \
            .where(Post.id.in_(
                sa.select(PostRespond.post_id).where(PostRespond.author_id == current_user.id)
            ))                                                                          \
            .where(
                sa.or_(
                    Post.selected == False,
                    Post.selected_respond_author_id == current_user.id
                )
            ) \
            .order_by(Post.selected.desc(), Post.update_date.desc())
    tasks = list(db.session.scalars(query))
    if current_user.check_role(['admin', 'teacher']):
        for task in tasks:
            respond_count = sa.select(func.count('*')).where(PostRespond.post_id == task.id)
            task.respond_count = db.session.scalar(respond_count)
    return render_template('post_list.html', tasks = tasks, create_new = True, null_message='У вас нету обьявлений')

@app.route('/')
@app.route('/index')
@app.route('/all-tasks/<filter>')
@app.route('/all-tasks/')
@app.route('/all-tasks')
def all_tasks(filter = None):
    query = sa.select(Post)                                 \
        .where(Post.selected == False)           \
        .where(Post.archived == False)                      \
        .order_by(Post.selected.desc(), Post.update_date.desc())
    tasks = list(db.session.scalars(query))
    if current_user.check_role(['admin', 'teacher']):
        for task in tasks:
            respond_count = sa.select(func.count('*')).where(PostRespond.post_id == task.id)
            task.respond_count = db.session.scalar(respond_count)
    return render_template('post_list.html', tasks = tasks, create_new = True, null_message='Сейчас на сайте обьявлений нет, приходите ещё')

@app.route('/')
@app.route('/archive/')
@app.route('/archive')
def archive(filter = None):
    query = sa.select(Post)                                         \
        .where(Post.archived == True)                               \
        .where(sa.or_(Post.author_id == current_user.id, Post.selected_respond_author_id == current_user.id)) \
        .order_by(Post.selected.desc(), Post.update_date.desc())
    return render_template('post_list.html', tasks = list(db.session.scalars(query)), create_new = False, title='Архив', null_message='В архиве пусто....')

@app.route('/create-post/', methods=['GET', 'POST'])
@app.route('/create-post',  methods=['GET', 'POST'])
@login_required
def create_post():
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.check_role('admin'):
        abort(418)
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
    return render_template('post.html', edit=True, form=form, data = data)

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
    if data.archived or data.selected:
        return redirect(url_for("post", id=post_id))
    return render_template('post.html', edit=True, form=form, data = data)

@app.route('/post/<id>', methods=['GET', 'POST'])
def post(id = None):
    data = db.session.scalar( sa.select(Post).where(Post.id == id) )
    if data is None:
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
        if respond and not data.selected:
            form.text.data = respond.text
            form.submit.label.text = "Изменить"
        if not respond:
            respond = PostRespond()
            respond.author = current_user
        responds = [respond]
        if data.selected and not respond.selected:
            return abort(418)
    else:
        form=''
        if current_user.is_authenticated and data.author_id == current_user.id:
            responds = data.respond
            responds = sorted(responds, key= lambda x: not x.selected)
        else:
            responds = []
    return render_template('post.html', edit=False, form=form, data=data, responds=responds)


@app.route('/archiving-post/<post_id>')
@login_required
def archiving_post(post_id):
    post = db.session.scalar( sa.select(Post).where(Post.id == post_id) )
    if post.author_id != current_user.id or post.selected:
        return abort(403)
    post.archived = True
    post.archived_date = func.now()
    db.session.commit()
    return redirect(url_for("post", id=post_id))

@app.route('/end-post/<post_id>')
@login_required
def end_post(post_id):
    post = db.session.scalar( sa.select(Post).where(Post.id == post_id) )
    if post.author_id != current_user.id or not post.selected:
        return abort(403)
    post.archived = True
    post.archived_date = func.now()
    db.session.commit()
    return redirect(url_for("post", id=post_id))

@app.route('/select_respond/post<post_id>&user<user_id>')
@login_required
def select_respond(post_id, user_id):
    post = db.session.scalar( sa.select(Post).where(Post.id == post_id) )
    if post.author_id != current_user.id:
        return abort(403)
    post.selected = True
    post.selected_date = func.now()
    post.selected_respond_author_id = user_id
    respond = db.session.query( PostRespond ).filter(PostRespond.author_id == user_id).filter(PostRespond.post_id == post_id).first()
    respond.selected = True
    db.session.commit()
    return redirect(url_for("post", id=post_id))




# admin actions

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.check_role('admin'):
        abort(418)
    users = db.session.scalars(sa.select(User))
    return render_template('admin/admin_panel.html', users=users)


@app.route('/admin/<user_id>', methods=['GET', 'POST'])
@login_required
def admin_panel_edit_user(user_id):
    if not current_user.check_role('admin'):
        abort(418)
    user = db.session.scalar(sa.select(User).where(User.id == user_id))
    form = AdminUserEditForm()
    if form.validate_on_submit():
        user.id         = form.id.data
        user.login      = form.login.data
        if form.password.data:
            user.set_password(form.password.data)
        user.name           = form.name.data
        user.aboutme        = form.aboutme.data
        user.contact_info   = form.contact_info.data
        user.account_type   = form.account_type.data
        db.session.commit()
        flash(['Данные сохранены', 'green'])
        return redirect(url_for("admin_panel"))
    form.aboutme.data = user.aboutme
    return render_template('admin/admin_user_edit.html', user=user, form=form)

@app.route('/admin-create-new-user')
def new_user():
    if not current_user.check_role('admin'):
        abort(418)
    if db.session.scalar(sa.select(User).where(User.login == 'new-user')) is not None:
        flash(['Новый пользователь уже создан', 'red'])
        return redirect(url_for("admin_panel"))
    u = User()
    u.login = 'new-user'
    u.set_password('new-user-password-change-it')
    db.session.add(u)
    db.session.commit()
    flash(['Вы добавили пользователя', 'green'])
    return redirect(url_for("admin_panel"))

@app.route('/admin-delete-user/<id>')
@login_required
def delete_user(id):
    if not current_user.check_role('admin'):
        abort(418)
    data = db.session.scalar( sa.select(User).where(User.id == id) )
    db.session.delete(data)
    db.session.commit()
    flash(['Вы удалили пользователя', 'green'])
    return redirect(url_for('admin_panel'))




# errors
@app.errorhandler(404)
def page_not_found_e(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(401)
def login_required_e(e):
    return render_template('errors/401.html'), 401

@app.errorhandler(403)
def Forbidden_e(e):
    return render_template('errors/403.html'), 401

@app.errorhandler(418)
def teapot_e(e):
    return render_template('errors/418.html'), 401




# api
@app.route('/api/get-notifications')
@login_required
def api_get_notifications():
    data = sa.select(Notification)                         \
            .where(Notification.reciver_id == current_user.id)   \
            .order_by(Notification.create_date.desc()).limit(5)
    data = list(db.session.scalars(data))
    return jsonify(*map(lambda x: x.json(), data))

@app.route('/api/ok-notifications')
@login_required
def api_ok_notifications():
    data = sa.select(Notification)                         \
        .where(Notification.reciver_id == current_user.id)   \
        .where(Notification.readed == False)
    data = list(db.session.scalars(data))
    print(data)
    for i in data:
        i.readed = True
    db.session.commit()
    return {'status' : 'ok'}

@app.route('/api/test-notification')
@login_required
def api_test_notification():
    current_user.add_notification('TEST NOTIFICATION', 'test notification sended')
    return {'status' : 'ok'}
