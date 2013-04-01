from flask import Blueprint, request

from utopia.handlers import *


index = Blueprint('index', __name__, template_folder='templates')

@index.route("/reflector")
def handle_reflect():
    # is there a better way to do this?
    ret = request.url_root + 'server.php'
    if ':5000' not in ret:
        ret = ret.replace('/server.php', ':5000/server.php')
    return ret


@index.route("/server.php", methods=['GET', 'POST'])
def server():
    action = request.values.get('action', '')
    handler = globals().get('handle_' + action, None)
    if handler is not None:
        ret = handler()
        ignored_keys = {'user_id', 'ticket_hmac', 'sequence_number'}
        value_string = '&'.join(('%s=%s' % (key, value)) for
                       key, value in request.values.iteritems()
                       if key not in ignored_keys)
        #app.logger.debug('%s %s \n%s', action, value_string, ret)
        return ret
    else:
        #app.logger.info('unknown action %r' % action)
        return 'DENIED'


