from flask import (render_template, request, g, redirect, url_for, jsonify,
                   flash)
from . import app, game_manager
from threading import Thread
from . import game_streamer, game_loader


class StopFlagRef:
    def __init__(self):
        self.stop = False

def create_cleanup_function(stop_flag_ref):
    def stop():
        stop_flag_ref.stop = True
    return stop


@app.route("/")
def scoreboard():
    print("doing stuffs")
    return render_template('scoreboard.html', users=[])


@app.route("/current_game")
def current_game():
    map_image = "Q3DM8.jpg"
    map_image_url = url_for('static', filename="img/" + map_image)
    return render_template('game_status.html', map_image_url=map_image_url)


@app.route("/stop_game", methods=['POST'])
def stop_game():
    if not game_manager.GMAccessor.game_exists():
        status = {"status": "Game not started"}
        return jsonify(status)

    game_manager.GMAccessor.stop_and_remove_instance()

    status = {"status": "Game Stopped"}
    return jsonify(status)


@app.route("/start_game", methods=['POST'])
def start_game():
    if game_manager.GMAccessor.game_exists():
        status = {"status": "Game already started"}
        return jsonify(status)

    stop_flag_ref = StopFlagRef()
    # create the new game. Accessors remembers the instances created
    game = game_manager.GMAccessor.create_instance(
        app.config["IOQUAKE_PATCH_DIR"],
        app.config["IOQUAKE_BASEQ3_DIR"],
        app.config["IOQUAKE_SERVER_EXE"],
        create_cleanup_function(stop_flag_ref)
    )

    game.start()

    t = Thread(target=game_streamer.read_from_queue,
               args=(game.game_output, stop_flag_ref))
    t.start()

    status = {"status": "we good foolio"}
    return jsonify(status)


# TODO: Limit upload directory to a finite size
@app.route('/upload_score', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('/'))
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect('/')
    if file:
        # do some song and dance to decode it. Performant? Naw but
        # easy to tweak later
        txt = file.stream.read()
        txt = txt.decode("utf-8")
        t = Thread(target=game_loader.load_from_text, args=(txt,))
        t.start()

    return redirect('/')
