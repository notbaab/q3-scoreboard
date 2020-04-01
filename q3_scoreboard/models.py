from . import db
from sqlalchemy.orm import relationship

BOT_PREFIX_NAME = "<bot>"
WORLD_ID = 1
WORLD_NAME = "<world>"


def init_db():
    db.create_all()
    # add our trusty bot and world users if they didn't exist
    world = User.query.get(WORLD_ID)
    if world is None:
        world = User(WORLD_NAME)
        db.session.add(world)
        db.session.commit()


def get_kills():
    db.session.query


class Weapon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    # could do this much better but...eh?
    @staticmethod
    def add_weapon_if_not_exists(weapon_id, weapon_name):
        if Weapon.query.get(weapon_id) is None:
            weapon = Weapon()
            weapon.id = weapon_id
            weapon.name = weapon_name
            db.session.add(weapon)
            db.session.commit()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def get_user_id(username):
        user = User.get_user_or_create_user()
        return user.id

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
    mapname = db.Column(db.String(80), nullable=False)
    time_started = db.Column(db.DateTime, nullable=False)
    time_finished = db.Column(db.DateTime)
    winner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    winner = relationship("User", foreign_keys=[winner_id])


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
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    killer = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    victum = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weapon_id = db.Column(db.Integer, db.ForeignKey('weapon.id'),
                          nullable=False)

    weapon = relationship("Weapon", foreign_keys=[weapon_id])

    def __init__(self, game_id, killer, victum, weapon_id):
        self.game_id = game_id
        self.killer = killer
        self.victum = victum
        self.weapon_id = weapon_id
