import os
from flask import Flask
from flask import Blueprint, request, session, redirect, render_template, url_for
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
        create = request.form.get("Create")
        if create == 'Create':
            return redirect(url_for('piazza.storycreate'))
    return render_template('piazza.html', userStatus=userStatus)

@piazza.route('/storycreate', methods=['POST', 'GET'])
def storycreate():
    if "email" not in session:
        session['oauth_origin'] = request.full_path
        return redirect(url_for('auth.login'))
    
    requestForm = RequestForm()
    if request.method == 'POST':
        # print(requestForm.data)
        create = request.form.get('create-request')
        cate = request.form.get('Category')
    
        title = requestForm.title.data
        info = requestForm.info.data

        # print(home, create, cate, title, info)

        button = buttonCheck(request.form)
        if button: return button

        if create == "create-request": 
            if cate == "": 
                return render_template('storycreate.html', form=requestForm, itemCategories=CATEGORY, categoryInvalid=True)
            else: 
                requestdb.createRequest(session["email"], title, cate, info)
                return redirect(url_for('piazza.home'))
    return render_template('storycreate.html')
