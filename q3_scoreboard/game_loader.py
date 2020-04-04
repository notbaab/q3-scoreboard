"""
Functions responsible for loading games from full server log files
"""
from . import models
from . import db
from datetime import datetime
from quake3_log_parser import parser


def get_user_id_from_username(username):
    user = models.User.get_user_or_create_user(username)
    return user.id


# returns the username or <BOT> of the player
def get_userid(player):
    username = player.name
    if player.is_bot:
        username = models.BOT_PREFIX_NAME + " " + player.name
    return get_user_id_from_username(username)


def load_game(game):
    print("adding game")
    game_model = models.Game()
    winner = game.get_leader()
    if winner is not None:
        game_model.winner_id = get_userid(winner)
    game_model.time_started = datetime.now()
    game_model.mapname = game.map_name

    # commit so we can get the game id
    db.session.add(game_model)
    db.session.commit()

    for stat_table in game.stat_table.values():
        # TODO: What to do about bots....Probably handle in the
        # load_stat_table_killl_entry
        load_kill_stat_table(game_model.id, stat_table)
        load_scores(game_model.id, stat_table)

    # load the disconnected players stat tables if they aren't bots
    for stat_table in game.disconnected_player_stat_table:
        if stat_table.player.is_bot:
            continue
        load_kill_stat_table(game_model.id, stat_table)


def load_from_text(input_data):
    games = parser.parse_str(input_data)

    for game in games:
        load_game(game)


# Do everything based on death so we have suicides added
def load_stat_table_kill_entry(game_id, kills, commit=False):
    for kill in kills:
        killer_id = get_userid(kill.killer)
        victum_id = get_userid(kill.victum)
        models.Weapon.add_weapon_if_not_exists(kill.kill_method,
                                               kill.kill_method_name)

        kill_entry = models.GameKill(game_id, killer_id, victum_id,
                                     kill.kill_method)
        db.session.add(kill_entry)
    if commit:
        db.session.commit()


def load_scores(game_id, stat_table):
    player_id = get_user_id_from_username(stat_table.player.name)
    score = models.Score(player_id, stat_table.score, game_id)
    db.session.add(score)
    db.session.commit()


def load_kill_stat_table(game_id, stat_table):
    # print(stat_table)
    for kills in stat_table.kill_by_player.values():
        load_stat_table_kill_entry(game_id, kills, False)
