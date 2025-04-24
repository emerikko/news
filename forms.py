from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    StringField, PasswordField, SubmitField,
    BooleanField, SelectField, TextAreaField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError
)

from data import db_session
from data.categories import Category
from data.articles import Article
from config import article_type_dict, article_status_dict
from utils import get_users_by_usernames

# --- Utility Functions ---


def get_category_choices():
    db_sess = db_session.create_session()
    return [(c.id, c.title) for c in db_sess.query(Category).all()]


def validate_editors_input(self, field):
    _, missing = get_users_by_usernames(field.data)
    if missing:
        raise ValidationError(f"Пользователи не найдены: {', '.join(missing)}")


# --- Auth Forms ---


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


# --- Article Forms ---


class ArticleCreateForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(min=1, max=255)])
    category = SelectField("Категория", coerce=int, validators=[DataRequired()])
    content_type = SelectField("Тип контента", coerce=str, choices=list(article_type_dict.items()),
                               validators=[DataRequired()])
    editors = StringField("Редакторы (юзернеймы через запятую)")
    submit = SubmitField("Создать")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = get_category_choices()


class ArticleEditForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(min=1, max=255)])
    subtitle = StringField("Подзаголовок", validators=[Length(max=255)])
    content = TextAreaField("Контент", validators=[DataRequired()])
    summary = TextAreaField("Сводка", validators=[DataRequired()])
    category_id = SelectField("Категория", coerce=int, validators=[DataRequired()])
    content_type = SelectField("Тип контента", coerce=str, choices=list(article_type_dict.items()),
                               validators=[DataRequired()])
    tags = StringField("Теги (через запятую)")
    status = SelectField("Статус", coerce=str, choices=list(article_status_dict.items()),
                         validators=[DataRequired()])
    submit = SubmitField("Подтвердить")

    def __init__(self, *args, **kwargs):
        article_id = kwargs.pop('article_id', None)
        super().__init__(*args, **kwargs)

        db_sess = db_session.create_session()
        self.category_id.choices = get_category_choices()

        if article_id:
            article = db_sess.query(Article).get(article_id)
            if article:
                self.title.data = article.title
                self.subtitle.data = article.subtitle
                self.content.data = article.content
                self.summary.data = article.summary
                self.category_id.data = article.category_id
                self.content_type.data = article.content_type
                self.tags.data = article.tags
                self.status.data = article.status


class ImageUploadForm(FlaskForm):
    image = FileField('Загрузка изображений', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения!')
    ])
    submit = SubmitField('Загрузить')


class NewCategoryForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired(), Length(min=1, max=255)])
    slug = StringField("Красивая ссылка", validators=[DataRequired(), Length(min=1, max=255)])
    description = TextAreaField("Описание", validators=[DataRequired()])
    submit = SubmitField("Создать")
