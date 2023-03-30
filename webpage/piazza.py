import os
from flask import Flask
from flask import Blueprint, request, session, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, buttonCheck, login_required
from db import itemdb, requestdb, accountdb, chatdb

piazza = Blueprint('piazza',__name__)

@piazza.route('/', methods=['POST', 'GET'])
def home():
    if "email" in session: userStatus = True
    else: userStatus = False

    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button
        create = request.form.get("Create")
        if create == 'Create':
            return redirect(url_for('piazza.storycreate'))
    return render_template('piazza.html', userStatus=userStatus)

@piazza.route('/storycreate', methods=['POST', 'GET'])
@login_required
def storycreate():
    return render_template('storycreate.html')
