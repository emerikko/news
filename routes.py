from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from data import db_session
from data.users import User
from data.categories import Category
from forms import RegisterForm, LoginForm

import config

routes = Blueprint('routes', __name__)


@routes.context_processor
def inject_user():
    return dict(authorized_user=current_user)


@routes.route('/')
def index():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    return render_template('user/index.html', categories=categories)


@routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(User).filter((User.username == form.username.data) | (User.email == form.email.data)).first():
            flash('Пользователь с таким именем пользователя или email уже существует', 'danger')
            return render_template('auth/register.html', form=form)

        user = User(
            username=form.username.data,
            email=form.email.data,
            hashed_password=generate_password_hash(form.password.data),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            pseudonym=form.pseudonym.data,
            email_verified=False,
            account_status='pending',
            role='user'
        )
        session.add(user)
        session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('routes.login'))

    return render_template('auth/register.html', form=form)


@routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and check_password_hash(user.hashed_password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Успешный вход. Добро пожаловать!', 'success')
            return redirect(request.args.get('next') or url_for('routes.index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('auth/login.html', form=form)


@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.', 'info')
    return redirect(url_for('routes.index'))


@routes.route('/profile/<identifier>')
def profile(identifier):
    session = db_session.create_session()
    user = session.query(User).filter(
        User.id == int(identifier) if identifier.isdigit() else User.username == identifier
    ).first()
    if not user:
        abort(404)
    return render_template('profile/user.html', user=user,
                           user_role_dict=config.user_role_dict,
                           user_status_dict=config.user_status_dict)


@routes.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
