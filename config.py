import os
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))
home = str(Path.home())

# Enable Flask's debugging features. Should be False in production
DEBUG = True
PREFERRED_URL_SCHEME = 'http'
HOST = "0.0.0.0"
SAVE_RAW_UPLOADED_FILES = True

IOQUAKE_PATCH_DIR = os.path.join(dir_path, "data", "mac", "baseq3")
IOQUAKE_BASEQ3_DIR = os.path.join(home, "Library/Application Support/Quake3/baseq3")
IOQUAKE_SERVER_EXE = ("/Applications/ioquake3/ioquake3.app/Contents/MacOS/"
                      "ioq3ded")

DATABASE_FILE = "data.db"
SQLALCHEMY_DATABASE_URI = "sqlite:////{}/{}".format(dir_path, DATABASE_FILE)
SQLALCHEMY_TRACK_MODIFICATIONS = False
LOG_DIR_LOC = os.path.join(dir_path, "game-logs")
