import os
from pathlib import Path

# configuration for running in the docker file. Paths are set to easy to
# volume points in the root directory of stuff
dir_path = os.path.dirname(os.path.realpath(__file__))
home = str(Path.home())

# Enable Flask's debugging features. Should be False in production
DEBUG = True
PREFERRED_URL_SCHEME = 'http'
HOST = "0.0.0.0"
SAVE_RAW_UPLOADED_FILES = True

# Path dir can be anywhere, it gets copied to the baseq3 dir on startup.
IOQUAKE_PATCH_DIR = "/patch-files"
IOQUAKE_BASEQ3_DIR = os.path.join(home, "ioquake3", "baseq3")
IOQUAKE_SERVER_EXE = os.path.join(home, "ioquake3", "ioq3ded.x86_64")

DATABASE_DIR = "/database"

DATABASE_FILE = "data.db"
SQLALCHEMY_DATABASE_URI = "sqlite:////{}/{}".format(DATABASE_DIR,
                                                    DATABASE_FILE)
SQLALCHEMY_TRACK_MODIFICATIONS = False
