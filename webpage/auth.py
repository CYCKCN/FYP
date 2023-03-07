from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for

from functools import wraps
from flask_login import LoginManager, login_user, logout_user, current_user

from utils import User
from db import accountdb

auth = Blueprint('auth', __name__)
    

@auth.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        email = request.form.get('usermail')
        password = request.form.get('password')
        submit = request.form.get('submit-button')

        # print(id, password, submit)

        if submit == "Submit": 
            loginInfo = accountdb.login(email, password)
            print(loginInfo)
            if "Login successfully!" in loginInfo:
                # username = accountdb.findUserName(email)
                login_user(User(email))
                return redirect(url_for('life.home'))

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    
    if request.method == 'POST':
        email = request.form.get('usermail')
        password = request.form.get('password')
        name = request.form.get('username')
        uni = request.form.get('Universities')
        submit = request.form.get('submit-button')

        account = accountdb.findUser(email)

        if account is None:
            signupInfo = accountdb.signup(name, password, email, uni)
            if "Err" not in signupInfo: login_user(User(email=email))
            return redirect(url_for('life.home'))
        else:
            # login_user(User(email=email))
            return "User Exists"
            
    return render_template('signup.html')

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))