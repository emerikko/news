from flask import Flask
from flask_login import LoginManager
from data import db_session
from data.users import User
import config

from routes import register_blueprints  # new import

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'meow_meow_meow'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.context_processor
def inject_user():
    from flask_login import current_user
    return dict(authorized_user=current_user)


def main():
    db_session.global_init("db/site.db")
    register_blueprints(app)
    app.run()


if __name__ == '__main__':
    main()
