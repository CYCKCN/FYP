from flask import Flask
from flask import Blueprint, session, request, abort, redirect, render_template, url_for

import requests
from pip._vendor import cachecontrol
import google.auth.transport.requests
from google.oauth2 import id_token

from functools import wraps
from utils import User, flow, GOOGLE_CLIENT_ID, buttonCheck
from db import accountdb

auth = Blueprint('auth', __name__)

@auth.route('/google_login', methods=['GET', 'POST'])
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button

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
                # login_user(User(email))
                # print(current_user.is_authenticated())
                return redirect(request.args.get('addr', url_for('life.home')))
        
        if home == "Home": 
            return redirect(url_for('life.home'))
        
        if signup == "signup": 
            return redirect(url_for('auth.signup'))

    return render_template('login.html')

@auth.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["email"] = id_info.get("email")
    session["name"] = id_info.get("name")

    account = accountdb.findUser(session["email"])
    if not account: signupInfo = accountdb.signup(session["name"], session["email"])
    return redirect(request.args.get('addr', url_for('life.home')))

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
    session.clear()
    return redirect(url_for('life.home'))