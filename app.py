from flask import Flask, render_template
from data import db_session

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'meow_meow_meow'


def main():
    db_session.global_init("db/site.db")
    app.run()


@app.route('/')
@app.route('/index')
def index():
    return render_template('user/index.html')


if __name__ == '__main__':
    main()
