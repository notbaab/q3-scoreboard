# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

server_config_name = "IOQ3_CONFIG"
# Initialize the app
app = Flask(__name__, instance_relative_config=True)

if server_config_name in os.environ:
    print("Using this config")
    app.config.from_envvar('IOQ3_CONFIG')
else:
    app.config.from_object('config')
    print("No config specified")

db = SQLAlchemy(app)


from . import views
# # Load the views and model
# #from app.models import models
