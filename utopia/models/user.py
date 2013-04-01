from utopia.app import db

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    secret = Column(String)

    # one-to-one
    state = db.relationship('UserState', uselist=False)
    # one-to-many
    houses = db.relationship('House', backref='user')
    # one-to-many, with explicit primaryjoin because there are multiple users
    robberies = db.relationship("Robbery",
                                primaryjoin="User.id==Robbery.victim_id",
                                backref='victim')

    def __init__(self, id=None, email=None):
        self.id = id
        self.email = email
        db.session.add(self)
        db.session.commit()
        state = UserState()
        state.user_id = self.id
        db.session.add(state)
        db.session.commit()

