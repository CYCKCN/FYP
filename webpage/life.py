from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from .auth import check_login

life = Blueprint('life',__name__)

@life.route('/home', methods=['POST', 'GET'])
# @check_login
def home():
    return render_template('home.html')

@life.route('/newlife', methods=['POST', 'GET'])
# @check_login
def newlife():
    return render_template('newlife.html')

@life.route('/item', methods=['POST', 'GET'])
# @check_login
def item():
    return render_template('item.html')