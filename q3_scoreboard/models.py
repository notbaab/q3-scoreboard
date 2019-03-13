from . import db

BOT_ID = 1
BOT_NAME = "<bot>"
WORLD_ID = 2
WORLD_NAME = "<world>"


def init_db():
    db.create_all()
    bot = User(BOT_NAME)
    world = User(WORLD_NAME)
    db.session.add(bot)
    db.session.commit()
    db.session.add(world)
    db.session.commit()


def get_kills():
    db.session.query


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def get_user_or_create_user(username):
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username)
            db.session.add(user)
            db.session.commit()
        return user


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mapname = db.Column(db.String(80))


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    score = db.Column(db.Integer)
    game_id = db.Column(db.Integer, db.ForeignKey("score.id"))

    def __init__(self, player_id, score, game_id):
        self.player_id = player_id
        self.score = score
        self.game_id = game_id


class GameKill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    killer = db.Column(db.Integer, db.ForeignKey('user.id'))
    victum = db.Column(db.Integer, db.ForeignKey('user.id'))
    method = db.Column(db.String(80))

    def __init__(self, game_id, killer, victum, method):
        self.game_id = game_id
        self.killer = killer
        self.victum = victum
        self.method = method
