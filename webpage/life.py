from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from .auth import check_login

life = Blueprint('life',__name__)

@life.route('/home', methods=['POST', 'GET'])
# @check_login
def home():
    if request.method == 'POST':
        submit = request.form.get('Sell')
        # print(submit)
        if submit == "Sell": 
            return redirect(url_for('life.sell'))
    return render_template('home.html')

@life.route('/sell', methods=['POST', 'GET'])
# @check_login
def sell():
    return render_template('sell.html')
    # return "Sell Page"

@life.route('/item', methods=['POST', 'GET'])
# @check_login
def item():
    return render_template('item.html')