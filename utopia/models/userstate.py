from utopia.app import db

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class UserState(db.Model):
    __tablename__ = 'userstates'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'), index=True)
    current_house_id = Column(ForeignKey('houses.id'))
    current_house = db.relationship('House')
