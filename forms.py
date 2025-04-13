from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length
# from data import db_session
# from data.categories import Category
# from config import article_name_dict


class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Подтвердите пароль', validators=[
        DataRequired(), EqualTo('password', message='Пароли должны совпадать')])
    first_name = StringField('Имя')
    last_name = StringField('Фамилия')
    pseudonym = StringField('Псевдоним')

    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

# TODO article stuff
