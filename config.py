import os
dir_path = os.path.dirname(os.path.realpath(__file__))

# Enable Flask's debugging features. Should be False in production
DEBUG = True
PREFERRED_URL_SCHEME = 'http'

DATABASE_FILE = "data.db"
SQLALCHEMY_DATABASE_URI = "sqlite:////{}/{}".format(dir_path, DATABASE_FILE)
SQLALCHEMY_TRACK_MODIFICATIONS = False
