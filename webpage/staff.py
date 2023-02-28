from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from .auth import check_login

staff = Blueprint('staff',__name__)

@staff.route('/', methods=['POST', 'GET'])
# @check_login
def main():
    return render_template('home.html')