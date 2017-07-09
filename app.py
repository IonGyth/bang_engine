import pickle
from uuid import uuid4

from datetime import timedelta
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
from game import Game
from player import AddPlayer, ShufflePlayers
from redis import Redis
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin

import daiquiri
daiquiri.setup()
logger = daiquiri.getLogger()


class RedisSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    serializer = pickle
    session_class = RedisSession

    def __init__(self, redis=None, prefix='session:'):
        if redis is None:
            redis = Redis()
        self.redis = redis
        self.prefix = prefix

    def generate_sid(self):
        return str(uuid4())

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        val = self.redis.get(self.prefix + sid)
        if val is not None:
            data = self.serializer.loads(val)
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.redis.delete(self.prefix + session.sid)
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.prefix + session.sid, val,
                         int(redis_exp.total_seconds()))
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True,
                            domain=domain)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def hello_world():
    logger.info('Serving root')
    return render_template('index.html')


@socketio.on('start_game')
def start_game():
    game = Game()
    game = AddPlayer(5).apply(game)
    game = ShufflePlayers().apply(game)

    emit('start_game', game.to_dict(), json=True)


@socketio.on('push_players')
def push_players(players):
    json_players = [{p.player_no: p.to_dict()} for p in players]

    logger.info('Pushing players')
    emit('push_players', json_players, json=True)


@socketio.on('my event')
def respondToRequest(message):
    logger.info('responding to request')
    emit('my response',{'data':'some response'})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=12000)
