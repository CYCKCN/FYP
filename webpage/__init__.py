import flask
import secrets
from flask import Flask, redirect, url_for
from flask_login import LoginManager

from db import connection, accountdb, itemdb, User
from utils import UPLOAD_FOLDER

class ConfigClass(object):
    SECRET_KEY = secrets.token_hex(16)
    USER_APP_NAME = "LIFE2"
    UPLOAD_FOLDER = UPLOAD_FOLDER
    # USER_ENABLE_EMAIL = False     
    # USER_ENABLE_USERNAME = True  
    # USER_REQUIRE_RETYPE_PASSWORD = False  

webpage = Flask(__name__)
webpage.config.from_object(ConfigClass)

login_manager = LoginManager()
login_manager.init_app(webpage)

@login_manager.user_loader
def user_loader(user_id):
    account = accountdb.findUser(user_id)
    if not account: return None
    return User(email=account["accountEmail"])


from .auth import auth
from .life import life

webpage.register_blueprint(life, url_prefix='/')
webpage.register_blueprint(auth, url_prefix='/auth')

@webpage.route("/")
def main():
    return redirect(url_for('life.home'))