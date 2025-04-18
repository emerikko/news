from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from data import db_session
from data.categories import Category
from config import article_type_dict, article_status_dict
from utils import get_users_by_usernames


# --- Auth forms ---


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

# --- Article forms ---


def validate_editors_input(self, field):
    _, missing = get_users_by_usernames(field.data)
    if missing:
        raise ValidationError(f"Пользователи не найдены: {', '.join(missing)}")


def category_choices():
    db_sess = db_session.create_session()
    return [(c.id, c.title) for c in db_sess.query(Category).all()]


class ArticleCreateForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(min=1, max=255)])
    category = SelectField("Категория", coerce=int, validators=[DataRequired()])
    content_type = SelectField("Тип контента", coerce=str, choices=list(article_type_dict.items()),
                               validators=[DataRequired()])
    editors = StringField("Редакторы (юзернеймы через запятую)")
    submit = SubmitField("Создать")

    def __init__(self, *args, **kwargs):
        super(ArticleCreateForm, self).__init__(*args, **kwargs)
        self.category.choices = category_choices()


class ArticleEditForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(min=1, max=255)])
    subtitle = StringField("Подзаголовок", validators=[Length(min=0, max=255)])
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
        from data import db_session
        from data.categories import Category
        from data.articles import Article

        article_id = kwargs.pop('article_id', None)
        super(ArticleEditForm, self).__init__(*args, **kwargs)

        db_sess = db_session.create_session()
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

        self.category_id.choices = [(c.id, c.title) for c in db_sess.query(Category).all()]

# TODO: Add forms for article deletion, comments, password recovery
