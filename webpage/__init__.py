import flask
import secrets
from flask import Flask, redirect, url_for
from flask_login import LoginManager

from db import connection, accountdb, User

class ConfigClass(object):
    SECRET_KEY = secrets.token_hex(16)
    USER_APP_NAME = "LIFE2" 
    # USER_ENABLE_EMAIL = False     
    # USER_ENABLE_USERNAME = True  
    # USER_REQUIRE_RETYPE_PASSWORD = False  

staffweb = Flask(__name__)
staffweb.config.from_object(ConfigClass)

login_manager = LoginManager()
login_manager.init_app(staffweb)

@login_manager.user_loader
def user_loader(user_id):
    account = accountdb.findUser(user_id)
    if not account: return None
    return User(id=account["accountID"], name=account["accountName"], auth=account["accountAuth"])

from .staff import staff
from .auth import auth

staffweb.register_blueprint(staff, url_prefix='/staff')
staffweb.register_blueprint(auth, url_prefix='/auth')

@staffweb.route("/")
def main():
    return redirect(url_for('auth.login'))