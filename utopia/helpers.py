import random
import string

from functools import wraps


class ResultFormatter(string.Formatter):

    def format(self, items, param_dict):
        format_string = '\n'.join('{%s}' % item for item in items.split())
        format_string += '\nOK\n'
        return self.vformat(format_string, [], param_dict)

    def convert_field(self, value, conversion):
        if conversion is None and isinstance(value, list):
            return format_list(value)
        return super(ResultFormatter, self).convert_field(value, conversion)


def get_row_dict(row):
    return {col: getattr(row, col) for col in row.__table__.columns.keys()}


def format_list(seq):
    return '#'.join(str(el).replace(' ', '_') for el in seq) or '#'


def int_to_alpha(num):
    ret = ''
    while num:
        ret += ord(ord('a'))

format_results = ResultFormatter().format


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



