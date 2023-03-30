import os
from flask import Flask
from flask import Blueprint, request, session, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, StoryForm, buttonCheck
from db import itemdb, requestdb, accountdb, chatdb, storydb

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
        return redirect(url_for('auth.google_login'))
    
    myItemList = itemdb.getItemList(user=session["email"])
    
    itemImg = ""
    storyForm = StoryForm()
    if request.method == 'POST':
        # print(requestForm.data)
        publish = request.form.get('Publish')
        itemID = request.form.get('selectedItem')

        info = storyForm.info.data

        if "upload_cont_img" in request.files: file = request.files['upload_cont_img']
        else: file = None
        image_path = ""        
        if file and file.filename != "" and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            itemImg = "../../" + image_path[8:]

        # print(home, create, cate, title, info)

        button = buttonCheck(request.form)
        if button: return button

        if publish == "Publish": 
            storydb.createStory(itemID, session["email"], image_path, info)
            return redirect(url_for('piazza.home'))
    return render_template('storycreate.html', form=storyForm, myItemList=myItemList, itemImg=itemImg)
