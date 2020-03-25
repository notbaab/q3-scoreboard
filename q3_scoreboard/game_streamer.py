from . import models
from . import db
from quake3_log_parser import lineparsers, tracker, datastructures


def get_user_id_from_username(username):
    user = models.User.get_user_or_create_user(username)
    return user.id


# returns the username of the player or BOT if a bot
def get_userid(player):
    if player.is_bot:
        return models.BOT_ID
    return get_user_id_from_username(player.name)


def handle_kill_line(game_tracker, game_db_id, line):
    killer_game_id, victum_game_id, method = lineparsers.parse_kill(line)
    killer = game_tracker.players.get(killer_game_id, None)
    victum = game_tracker.players.get(victum_game_id, None)

    killer_id = get_userid(killer)
    victum_id = get_userid(victum)
    kill_entry = models.GameKill(game_db_id, killer_id, victum_id, method)
    db.session.add(kill_entry)


def add_final_score(player_id, score, game_id):
    score = models.Score(player_id, score, game_id)
    db.session.add(score)
    db.session.commit()


def read_game_from_queue(game_start_data, queue, stop_flag):
    """Continually read from the queue and stream out the updates to the db
    """
    game_model = models.Game()
    game_model.mapname = game_start_data["mapname"]
    db.session.add(game_model)

    # commit so we can get the game id
    db.session.commit()
    game_id = game_model.id

    # need the game tracker cause it keeps the mapping of player id to
    # username. I'm not happy about this, it should be gooder
    game_tracker = datastructures.Game(game_model.mapname)

    while not stop_flag.stop:
        line = queue.get()
        line_type = lineparsers.get_line_type(line)

        if line_type is None:
            continue

        # parse it for the tracker
        if line_type == lineparsers.LineType.GAME_SHUTDOWN:
            print("game is done")
            game_tracker.print_summary()
            return

        tracker.track_functions[line_type](game_tracker, line)

        if line_type == lineparsers.LineType.PLAYER_INFO:
            player = lineparsers.parse_player_added(line)
            if not player.is_bot:
                # TODO: Don't rely on this to add a new user to the database
                get_userid(player)
        elif line_type == lineparsers.LineType.KILL:
            handle_kill_line(game_tracker, game_id, line)
        elif line_type == lineparsers.LineType.SCORE:
            player_id_in_game, score = lineparsers.parse_final_score(line)
            # the final score parser only returns the local game id, use it
            # to get the player name. Even though the final score line has the
            # playername in it
            player_tracker = game_tracker.players.get(player_id_in_game, None)
            if player_tracker is None:
                print("something fucky happened, couldn't find %s" %
                      player_tracker.name)
                continue
            print("adding player score for %s " % player_tracker.name)
            player_database_id = get_userid(player_tracker)
            add_final_score(player_database_id, score, game_id)


def read_from_queue(queue, stop_flag):
    """Continually read from the queue and stream out the updates to the db
    """
    print("Loading from queue")
    # no close method on the queue so just gotta wait until we get the stop
    # signal
    while not stop_flag.stop:
        # grab the game
        line = queue.get()
        line_type = lineparsers.get_line_type(line)
        if line_type == lineparsers.LineType.INIT_GAME:
            print("Game Started")
            game_data = lineparsers.parse_start_game(line)
            print(game_data)
            read_game_from_queue(game_data, queue, stop_flag)
