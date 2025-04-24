from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from data import db_session
from data.users import User
from forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        with db_session.create_session() as db_sess:
            user_exists = db_sess.query(User).filter(
                (User.username == form.username.data) |
                (User.email == form.email.data)
            ).first()

            if user_exists:
                flash('Пользователь с таким именем или email уже существует.', 'danger')
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
            db_sess.add(user)
            db_sess.commit()

        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        with db_session.create_session() as db_sess:
            user = db_sess.query(User).filter(User.username == form.username.data).first()

        if user and check_password_hash(user.hashed_password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Добро пожаловать!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))

        flash('Неверное имя пользователя или пароль.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно вышли из аккаунта.', 'info')
    return redirect(url_for('main.index'))
