from utopia.app import db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class House(db.Model):
    __tablename__ = 'houses'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'), index=True)

    house_map = Column(String)
    name = Column(String)
    vault_contents = Column(String)
    backpack_contents = Column(String)
    gallery_contents = Column(String)
    current_balance = Column(Integer)
    wife_money = Column(Integer)
    must_self_test = Column(Integer)
    music_seed = Column(Integer)
    wife_name = Column(String)
    son_name = Column(String)
    daughter_name = Column(String)
    payment_count = Column(Integer)
    you_paid_total = Column(Integer)
    wife_paid_total = Column(Integer)

    def __init__(self, user_id, last_house=None):
        self.user_id = user_id

        if last_house is not None:
            # copy over from the previous house
            for column, value in get_row_dict(last_house).iteritems():
                setattr(self, column, value)
            self.id = None  # ... but not id
        else:
            self.house_map = self.get_default_map()
            self.name = '@%d' % user_id
            self.vault_contents = '#'
            self.backpack_contents = '#'
            self.gallery_contents = '#'
            self.current_balance = 100000
            self.wife_money = 100000
            self.must_self_test = 1
            self.music_seed = random.randint(0, 1000000)
            self.wife_name = 'Wife'
            self.son_name = 'Son'
            self.daughter_name = 'Daughter'
            self.payment_count = 0
            self.you_paid_total = 0
            self.wife_paid_total = 0

    def get_default_map(self):
        cells = {}
        for n in range(32):
            cells[n, 0] = 998
            cells[n, 31] = 998
            cells[0, n] = 998
            cells[31, n] = 998
        cells[0, 16] = 0
        cells[8, 15] = 999  # vault
        cells[7, 18] = 1010
        cells[5, 18] = 1020
        cells[9, 18] = 1040
        ret = []
        for y in range(32):
            for x in range(32):
                ret.append(cells.get((x, y), 0))
        return '#'.join(map(str, ret))

    def format_edit(self):
        data = get_row_dict(self)
        data['price_list'] = ('1:1@10#2@20#3@50#0@0#21@20#20@15#111@100'
                              '#103@200#102@5#51@20#101@50#108@50#100@50'
                              '#107@50#106@10#104@20#105@20#30@100#110@50'
                              '#112@200#70@200#71@100#72@20#500@20#509@20'
                              '#501@100#502@470#503@2#504@26#505@6#506@20'
                              '#507@50#508@8#510@2#511@60'
                              ':todo_hash_this_when_capitalist')
        items = ('house_map vault_contents backpack_contents'
                 ' gallery_contents price_list current_balance'
                 ' must_self_test music_seed wife_name son_name daughter_name'
                 ' payment_count you_paid_total wife_paid_total')
        return format_results(items, data)

    def format_rob(self):
        data = get_row_dict(self)
        items = ('name house_map backpack_contents gallery_contents'
                 ' wife_money music_seed wife_name son_name daughter_name')
        return format_results(items, data)


