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


GAME_SCORE = ("SELECT user.username, score.score, user.id FROM score, "
              "user WHERE score.game_id = :id "
              "AND user.id = score.player_id")

LEADERBOARD = ("SELECT user.username, sum(score.score), "
               "count(score.game_id), user.id FROM score, user WHERE "
               "user.id = score.player_id GROUP BY score.player_id")

CARNAGE = ("SELECT user.username, sum(score.score), "
           "count(score.game_id) FROM score, user WHERE "
           "user.id = score.player_id and user.id = :id")

KILLED_MOST = """
SELECT count(game_kill.id), user.username FROM game_kill, \
user WHERE user.id = game_kill.victum and game_kill.killer = :id \
GROUP BY game_kill.victum ORDER BY count(game_kill.id) DESC
"""

KILLED_BY = """
SELECT count(game_kill.id), user.username FROM game_kill, \
user WHERE user.id = game_kill.killer and game_kill.victum = :id \
GROUP BY game_kill.killer ORDER BY count(game_kill.id) DESC
"""

TOOL_OF_DESTRUCTION = """
SELECT count(weapon.id), weapon.name FROM game_kill, weapon, \
user WHERE user.id = game_kill.killer and weapon.id = game_kill.weapon_id and \
user.id = 7 GROUP BY weapon.id ORDER BY count(weapon.id) DESC
"""

GAME_HISTORY = """
SELECT game.time_started, game.mapname, score.score, game.id FROM score, user,\
game WHERE user.id = score.player_id  and score.game_id = game.id and \
user.id = :id ORDER BY game.time_started DESC
"""


def get_user_profile(session, user_id):
    profile = {}
    user = User.query.get(user_id)
    if user is None:
        return None

    profile["name"] = user.username
    weapon_stats = session.execute(TOOL_OF_DESTRUCTION,
                                   {'id': user_id}).fetchall()
    profile["weapon_stats"] = weapon_stats

    game_history = session.execute(GAME_HISTORY, {'id': user_id}).fetchall()
    kill_table = session.execute(KILLED_MOST, {'id': user_id}).fetchall()
    victum_table = session.execute(KILLED_BY, {'id': user_id}).fetchall()
    carnage = session.execute(CARNAGE, {'id': user_id}).fetchall()[0]

    profile["weapon_stats"] = []
    profile["game_history"] = []
    profile["kill_table"] = []
    profile["victum_table"] = []
    profile["carnage"] = {}

    # do some gross clean up of everything before adding it. Probably
    # can do this is sqlaclchemy but I dont' want to at the moment. At
    # least this creates a good view if we want to change it later
    for game in game_history:
        profile["game_history"].append({
            "time": game[0],
            "mapname": game[1],
            "score": game[2],
            "id": game[3]
        })

    for kill in kill_table:
        profile["kill_table"].append({
            "count": kill[0],
            "user": kill[1],
        })

    for victum in victum_table:
        profile["victum_table"].append({
            "count": victum[0],
            "user": victum[1],
        })

    for weapon in weapon_stats:
        weapon_parts = weapon[1].split("_")
        pretty_name = " ".join(weapon_parts[1:])
        profile["weapon_stats"].append({
            "kills": weapon[0],
            "weapon": pretty_name
        })

    profile["carnage"]["total_kills"] = carnage[1]
    profile["carnage"]["total_games"] = carnage[2]
    profile["carnage"]["ratio"] = carnage[1] / float(carnage[2])

    return profile


def get_score(session, game_id):
    # session.query(Game).where()
    game = Game.query.get(game_id)
    return_dict = {
        "map": game.mapname,
        "players": []
    }
    results = session.execute(GAME_SCORE, {'id': game_id}).fetchall()
    for result in results:
        username, score, id = result
        player_dict = {
            "username": username,
            "score": score,
            "id": id
        }
        return_dict["players"].append(player_dict)

    return return_dict


def get_leaderboard(session):
    players = []

    results = session.execute(LEADERBOARD)
    for result in results:
        username, total_kills, games_played, id = result
        player_dict = {
            "username": username,
            "id": id,
            "kills": total_kills,
            "games_played": games_played,
            "average_score_per_game": total_kills / float(games_played)
        }
        players.append(player_dict)

    return players


def query_db(conn, query, args=(), one=False):
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
