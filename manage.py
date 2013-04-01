import sys
import os
#sys.path.append(os.path.join(os.path.dirname(__file__), "utopia"))

from flask.ext.script import Manager

from utopia.app import create_app, db

manager = Manager(create_app)


@manager.command
def dropdb():
    """Drops Database
    """
    db.drop_all()
    print "DB DROPPED"


@manager.command
def createdb():
    """Creates Database
    """
    db.create_all()
    print "DB CREATED"


if __name__ == '__main__':
    manager.run()
