from utopia.app import db

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from utopia.helpers import format_results



class Robbery(db.Model):
    __tablename__ = 'robberies'

    id = Column(Integer, primary_key=True)

    victim_id = Column(ForeignKey('users.id'), index=True)
    robber_id = Column(ForeignKey('users.id'))
    house_id = Column(ForeignKey('houses.id'))
    house = db.relationship('House')

    name = Column(String)

    final_map = Column(String)
    backpack_contents = Column(String)
    move_list = Column(String)

    loot_value = Column(Integer)
    wife_money = Column(Integer)

    def __init__(self, user, previous_house, final_map,
                 move_list, backpack_contents):
        self.robber_id = user.id
        self.victim_id = previous_house.user_id
        self.house_id = previous_house.id
        self.final_map = final_map
        self.move_list = move_list
        self.backpack_contents = backpack_contents
        self.loot_value = 0
        self.wife_money = 0

        self.name = '@%d' % self.robber_id

    def format_log(self):
        data = get_row_dict(self.house)
        data.update(get_row_dict(self))
        data['victim_name'] = self.house.name

        items = ('name victim_name house_map'
                 ' backpack_contents move_list loot_value wife_money'
                 ' music_seed wife_name son_name daughter_name')
        return format_results(items, data)

