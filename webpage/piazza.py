import os
from flask import Flask
from flask import Blueprint, request, session, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, buttonCheck
from db import itemdb, requestdb, accountdb, chatdb

piazza = Blueprint('piazza',__name__)

@piazza.route('/', methods=['POST', 'GET'])
def home():
    if "email" in session: userStatus = True
    else: userStatus = False

    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button
    return render_template('piazza.html', userStatus=userStatus)