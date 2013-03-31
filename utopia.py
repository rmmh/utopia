#!/usr/bin/python
import random
import string

from functools import wraps

from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)


def get_row_dict(row):
    return {col: getattr(row, col) for col in row.__table__.columns.keys()}


def format_list(seq):
    return '#'.join(str(el).replace(' ', '_') for el in seq) or '#'


def int_to_alpha(num):
    ret = ''
    while num:
        ret += ord(ord('a'))


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


class UserState(db.Model):
    __tablename__ = 'userstates'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'), index=True)
    current_house_id = Column(ForeignKey('houses.id'))
    current_house = db.relationship('House')


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


class ResultFormatter(string.Formatter):

    def format(self, items, param_dict):
        format_string = '\n'.join('{%s}' % item for item in items.split())
        format_string += '\nOK\n'
        return self.vformat(format_string, [], param_dict)

    def convert_field(self, value, conversion):
        if conversion is None and isinstance(value, list):
            return format_list(value)
        return super(ResultFormatter, self).convert_field(value, conversion)

format_results = ResultFormatter().format


@app.route("/server.php", methods=['GET', 'POST'])
def server():
    action = request.values.get('action', '')
    handler = globals().get('handle_' + action, None)
    if handler is not None:
        ret = handler()
        ignored_keys = {'user_id', 'ticket_hmac', 'sequence_number'}
        value_string = '&'.join(('%s=%s' % (key, value)) for
                       key, value in request.values.iteritems()
                       if key not in ignored_keys)
        app.logger.debug('%s %s \n%s', action, value_string, ret)
        return ret
    else:
        app.logger.info('unknown action %r' % action)
        return 'DENIED'


def handle_debug():
    raise ValueError


@app.route("/reflector")
def handle_reflect():
    # is there a better way to do this?
    ret = request.url_root + 'server.php'
    if ':5000' not in ret:
        ret = ret.replace('/server.php', ':5000/server.php')
    return ret


def authenticate(func):
    @wraps(func)
    def authenticated_function(*args, **kwargs):
        user_id = int(request.values['user_id'])
        user = db.session.query(User).get(user_id)
        if user is None:
            user = User(id=user_id, email='%d@unknown' % user_id)
        if user.secret is not None:
            sequence_number = request.values['sequence_number']
            ticket_hmac = request.values['ticket_hmac']
            if hmac(user.secret, sequence_number) != ticket_hmac:
                return 'DENIED'
        request.user = user
        return func(*args, **kwargs)
    return authenticated_function


def handle_check_user():
    email = request.values['email']
    users = db.session.query(User).filter_by(email=email).all()
    if not users:   # new user, inject
        user = User(email=email)
    else:
        user = users[0]
    minVersionNumber = 5
    userID = user.id
    sequenceNumber = 0
    adminStatus = 0
    return format_results('minVersionNumber userID sequenceNumber'
                          ' adminStatus', locals())


@authenticate
def handle_check_hmac():
    return 'OK'


@authenticate
def handle_start_edit_house():
    if len(request.user.houses) == 0:
        house = House(request.user.id)
        db.session.add(house)
        db.session.commit()
    else:
        house = request.user.houses[-1]
    return house.format_edit()


@authenticate
def handle_start_self_test():
    return 'OK'


@authenticate
def handle_end_self_test():
    return 'OK'


@authenticate
def handle_end_edit_house():
    '''
    Inputs:
        &died=[0 or 1]
        &house_map=[house map]
        &vault_contents=[vault contents]
        &backpack_contents=[bp contents]
        &gallery_contents=[gal contents]
        &price_list=[price list]
        &purchase_list=[purchase list]
        &sell_list=[sell list]
        &self_test_move_list=[move list]
        &family_exit_paths=[paths]
    '''
    last_house = request.user.houses[-1]
    # if nothing changed, don't save it
    val = request.values
    if val['purchase_list'] == '#' and val['sell_list'] == '#' \
            and val['house_map'] == last_house.house_map:
        return 'OK'

    # create a new house to save all this
    house = House(request.user.id, last_house)

    house.house_map = val['house_map']
    house.vault_contents = val['vault_contents']
    house.backpack_contents = val['backpack_contents']
    house.gallery_contents = val['gallery_contents']
    house.must_self_test = 0
    db.session.add(house)
    db.session.commit()
    return 'OK'


@authenticate
def handle_ping_house():
    return 'OK'


@authenticate
def handle_list_houses():
    '''
    Inputs:
         &skip=[number]
         &limit=[number]
         &name_search=[single word]
    Returns:
    user_id#character_name#last_robber_name#loot_value#rob_attempts#rob_deaths
    ....
    more_pages
    OK
    '''

    skip = int(request.values['skip'])
    limit = int(request.values['limit'])
    search = request.values['name_search']

    house_query = db.session.query(House)
    houses = house_query.order_by('current_balance').slice(skip, limit)

    targets = []

    for house in houses:
        # note that we're returning house_id instead of user_id,
        # so you can rob a specific instance of a house
        targets.append([house.id, '%s (%d)' % (house.name, house.id), '',
                        house.current_balance, 0, 0])

    lines = '\n'.join(map(format_list, targets))
    more_pages = int(len(house_query.all()) > skip + limit + 1)

    return format_results('lines more_pages', locals())


@authenticate
def handle_list_logged_robberies():
    '''
    Inputs:
           &skip=[number]
           &limit=[number]
           &name_search=[single word]
    Returns:
    log_id#character_name#last_robber_name#loot_value#rob_attempts#rob_deaths
    ....
    more_pages
    OK
    '''
    skip = int(request.values['skip'])
    limit = int(request.values['limit'])
    search = request.values['name_search']

    targets = []

    robberies = request.user.robberies

    for robbery in robberies[skip: skip + limit]:
        targets.append([robbery.id, '', robbery.name,
                        robbery.loot_value, 0, 0])

    lines = '\n'.join(map(format_list, targets))
    more_pages = int(len(robberies) > skip + limit + 1)

    return format_results('lines more_pages', locals())


@authenticate
def handle_start_rob_house():
    request.user.state.current_house_id = request.values['to_rob_user_id']
    db.session.commit()
    return request.user.state.current_house.format_rob()


@authenticate
def handle_end_rob_house():
    '''
    Inputs:
       &success=[0(die) or 1(hit vault) or 2(leave)]
       &wife_killed=[0/1]
       &wife_robbed=[0/1]
       &any_family_killed=[0/1]
       &backpack_contents=[contents]
       &move_list=[move list]
       &house_map=[house map]
    '''

    previous_house = request.user.state.current_house

    robbery = Robbery(request.user, previous_house,
                      request.values['house_map'],
                      request.values['move_list'],
                      request.values['backpack_contents'])
    db.session.add(robbery)
    db.session.commit()

    money_taken = 0
    stuff_taken = []
    gallery_stuff_taken = []

    return format_results('money_taken stuff_taken gallery_stuff_taken',
                          locals())


@authenticate
def handle_get_robbery_log():
    log_id = request.values['log_id']
    robbery = db.session.query(Robbery).get(log_id)

    if robbery.victim != request.user:
        return 'DENIED'

    return robbery.format_log()

if __name__ == "__main__":
    # db.drop_all()
    db.create_all()
    app.run("0.0.0.0", use_reloader=True)
