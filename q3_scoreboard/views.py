from flask import (render_template, request, g, redirect, url_for, jsonify,
                   flash)
from . import app, game_manager
from threading import Thread
from . import dataloader


@app.route("/")
def scoreboard():
    print("doing stuffs")
    return render_template('scoreboard.html', users=[])


@app.route("/current_game")
def current_game():
    map_image = "Q3DM8.jpg"
    map_image_url = url_for('static', filename="img/" + map_image)
    return render_template('game_status.html', map_image_url=map_image_url)


@app.route("/start_game", methods=['POST'])
def start_game():
    game = game_manager.GameManager(app.config["IOQUAKE_BASE_DIRECTORY"])
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
        # as_lines = txt.decode("utf-8").split("\n")
        txt = txt.decode("utf-8")
        t = Thread(target=dataloader.load_from_text, args=(txt,))
        t.start()
        # parser.parse_lines(as_lines)

    return redirect('/')
