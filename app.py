import os
from flask import Flask
from flask_login import LoginManager, current_user

from data import db_session
from data.users import User
from routes import register_blueprints


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = 'meow_meow_meow'

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        user = db_sess.get(User, user_id)
        db_sess.close()
        return user

    @app.context_processor
    def inject_user():
        return dict(authorized_user=current_user)

    register_blueprints(app)
    return app


db_session.global_init("db/site.db")
app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
