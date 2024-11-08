from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, MultipleFileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    code = StringField('Код', validators=[DataRequired()])
    name = StringField('ФИО', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Завершить')

class ProfileEditorForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    aboutme = TextAreaField('Обомне', validators=[DataRequired()])
    contact_info = TextAreaField('contact_info')
    photo = FileField('image', validators=[FileAllowed(['jpg', 'png', 'webp', 'gif','jpeg'], 'Images only!')])
    submit = SubmitField('Завершить')

class PostEditorForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    coast = StringField('Цена')
    currency = StringField('Валюта')
    data = StringField('Описание')
    data_text = StringField('Описание текст')
    files = MultipleFileField() # todo
    submit = SubmitField('Завершить')


class PostRespondForm(FlaskForm):
    text = TextAreaField('Откликнутся', validators=[DataRequired()])
    submit = SubmitField('Откликнутся')


class AdminUserEditForm(FlaskForm):
    id = StringField('id')
    login = StringField('login')
    password = StringField('password')
    name = StringField('name')
    aboutme = TextAreaField('Обомне', validators=[DataRequired()])
    contact_info = TextAreaField('contact_info')
    account_type = StringField('account_type')
    submit = SubmitField('Подтвердить')

class PortfolioRecordForm(FlaskForm):
    data = TextAreaField('Информация', validators=[DataRequired()])
    submit = SubmitField('Отправить отклик')