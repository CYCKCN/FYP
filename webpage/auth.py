from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for

from functools import wraps
from flask_login import LoginManager, login_user, logout_user, current_user

from utils import User
from db import accountdb

auth = Blueprint('auth', __name__)

# def check_login():
#     if not current_user.is_authenticated: 
#         return redirect(url_for('auth.login'))
    

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated: 
        return redirect(url_for('home.main'))
    
    # if request.method == 'POST':
    #     id = request.form.get('username')
    #     password = request.form.get('password')
    #     submit = request.form.get('submit-button')

    #     print(id, password, submit)

    #     if submit == "Submit": 
    #         loginInfo = accountdb.login(id, password, "STAFF")
    #         print(loginInfo)
    #         if "Login successfully!" in loginInfo:
    #             username = accountdb.findUserName(id)
    #             login_user(User(id, username, "STAFF"))
    #             return redirect(url_for('staff.main'))

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))