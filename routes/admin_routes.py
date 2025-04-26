from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from data import db_session
from data.categories import Category
from forms import NewCategoryForm


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    if not current_user.role == 'admin':
        return redirect(url_for('main.index'))

    form = NewCategoryForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        category = db_sess.query(Category).filter_by(title=form.title.data).first()
        if category:
            flash('Категория с таким именем уже существует.', 'danger')
        category = db_sess.query(Category).filter_by(slug=form.slug.data).first()
        if category:
            flash('Категория с такой ссылкой уже существует.', 'danger')
        else:
            category = Category(title=form.title.data, slug=form.slug.data, description=form.description.data)
            db_sess.add(category)
            db_sess.commit()
            flash('Категория успешно создана.', 'success')
        db_sess.close()
        return redirect(url_for('main.index'))

    return render_template('categories/new_category.html', form=form)


@admin_bp.route('/category/<string:slug>/delete/', methods=['POST', 'GET'])
@login_required
def delete_category(slug):
    if not current_user.role == 'admin':
        return redirect(url_for('main.index'))

    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter_by(slug=slug).first()
    if category:
        db_sess.delete(category)
        db_sess.commit()
        flash('Категория успешно удалена.', 'success')
    else:
        flash('Категория не найдена.', 'danger')
    db_sess.close()
    return redirect(url_for('main.index'))