#!/usr/bin/python
import random
import string

from functools import wraps

from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy

from extensions import db
from views import index


def create_app():

    app = Flask(__name__)
    app.config.from_object('utopia.settings')

    db.init_app(app)

    app.register_blueprint(index)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run("0.0.0.0", use_reloader=True)
