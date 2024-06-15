from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, MultipleFileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class ProfileEditorForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    aboutme = TextAreaField('Обомне', validators=[DataRequired()])
    photo = FileField('image', validators=[FileAllowed(['jpg', 'png', 'webp', 'gif'], 'Images only!')])
    submit = SubmitField('Завершить')

class PostEditorForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    coast = FloatField('Цена')
    currency = StringField('Валюта')
    data = StringField('Описание', validators=[DataRequired()])
    data_text = StringField('Описание текст', validators=[DataRequired()])
    files = MultipleFileField() # todo
    submit = SubmitField('Завершить')
