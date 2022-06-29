import flask
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '16svjEOQ4IsJj6P4LUH8jw'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

from yt import routes