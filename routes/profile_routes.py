from flask import Blueprint, render_template, abort
from data import db_session
from data.users import User
import config

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile/<identifier>')
def profile(identifier):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.id == int(identifier) if identifier.isdigit() else User.username == identifier
    ).first()
    if not user:
        abort(404)
    return render_template('profile/user.html',
                           user=user,
                           user_role_dict=config.user_role_dict,
                           user_status_dict=config.user_status_dict)

# TODO: Make profile edit
