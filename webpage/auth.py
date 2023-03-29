from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for

from functools import wraps
from flask_login import LoginManager, login_user, logout_user, current_user

from utils import User
from db import accountdb

auth = Blueprint('auth', __name__)
    

@auth.route('/login', methods=['GET', 'POST'])
def login():

    # print(current_user.is_authenticated)
    
    if request.method == 'POST':
        email = request.form.get('usermail')
        password = request.form.get('password')
        submit = request.form.get('submit-button')
        home = request.form.get('Home')
        signup = request.form.get('signup')

        # print(signup)

        if submit == "Submit": 
            loginInfo = accountdb.login(email, password)
            # print(loginInfo)
            if "Login successfully!" in loginInfo:
                # username = accountdb.findUserName(email)
                login_user(User(email))
                # print(current_user.is_authenticated())
                return redirect(request.args.get('addr', url_for('life.home')))
        
        if home == "Home": 
            return redirect(url_for('life.home'))
        
        if signup == "signup": 
            return redirect(url_for('auth.signup'))

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    
    if request.method == 'POST':
        email = request.form.get('usermail')
        password = request.form.get('password')
        name = request.form.get('username')
        uni = request.form.get('Universities')
        submit = request.form.get('submit-button')
        home = request.form.get('Home')
        login = request.form.get('login')

        account = accountdb.findUser(email)

        if submit == "Submit":
            if account is None:
                signupInfo = accountdb.signup(name, password, email, uni)
                if "Err" not in signupInfo: login_user(User(email))
                else: return signupInfo
                return redirect(url_for('life.home'))
            else:
                # login_user(User(email=email))
                return "User Exists"
            
        if home == "Home": 
            return redirect(url_for('life.home'))
        
        if login == "login": 
            return redirect(url_for('auth.login'))
            
    return render_template('signup.html')

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('life.home'))