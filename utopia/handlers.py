from flask import request
from utopia.app import db
from utopia.helpers import format_results, authenticate
from utopia.models import User, House, Robbery, User, UserState


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


def handle_debug():
    raise ValueError


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

