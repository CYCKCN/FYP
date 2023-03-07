import os
from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, RequestForm
from db import itemdb, requestdb, accountdb

life = Blueprint('life',__name__)

@life.route('/home', methods=['POST', 'GET'])
def home():
    
    itemInfo = itemdb.getItemList()
    requestInfo = requestdb.getRequestList()
    # print(itemInfo)
    if request.method == 'POST':
        sell = request.form.get('Sell')
        buy = request.form.get('Request')
        login = request.form.get('Login')
        signup = request.form.get('Signup')
        profile = request.form.get('Profile')

        # print(submit)
        if sell == "Sell": 
            return redirect(url_for('life.sell'))

        if buy == "Request": 
            return redirect(url_for('life.buy'))
        
        if login == "Login": 
            return redirect(url_for('auth.login'))
        
        if signup == "Signup": 
            return redirect(url_for('auth.signup'))

        if profile == "Profile": 
            return redirect(url_for('life.profile'))
    
    if current_user.is_authenticated: userStatus = True
    else: userStatus = False

    return render_template('home.html', itemInfo=itemInfo, requestInfo=requestInfo, userStatus=userStatus, itemCategories=CATEGORY)

@life.route('/sell', methods=['POST', 'GET'])
# @check_login
def sell():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        home = request.form.get('Home')
        profile = request.form.get('Profile')
        submit = request.form.get('create-contract')
        name = request.form.get('Name')
        price = request.form.get('Price')
        category = request.form.get('Category')
        info = request.form.get('Description')
        # print(request.files)
        if "upload_cont_img" in request.files: file = request.files['upload_cont_img']
        else: file = None
        image_path = ""

        # print(name, price, category, info)
        # print(submit)

        if home == "Home": 
            return redirect(url_for('life.home'))
        
        if profile == "Profile": 
            return redirect(url_for('life.profile'))
        
        if file and file.filename != "" and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = os.path.join(UPLOAD_FOLDER, filename)
        # print(image_path)
        if submit == "new-contract":
            itemdb.createItem('-1', name, price, category, info, image_path)
            return redirect(url_for('life.home'))

    return render_template('sell.html')
    # return "Sell Page"

@life.route('/item/<itemID>', methods=['POST', 'GET'])
# @check_login
def item(itemID):
    item = itemdb.findItem(itemID)
    if item:
        name, cate, price, des, path = item['itemName'], item['itemCate'], item['itemPrice'], item['itemInfo'], item['itemImg']
    else:
        return "Record not found", 400
    
    if request.method == 'POST':
        home = request.form.get('Home')
        sell = request.form.get('Sell')

        if home == "Home": 
            return redirect(url_for('life.home'))
        
        if sell == "Sell": 
            return redirect(url_for('life.sell'))

    return render_template('item.html', item_name=name, item_category=cate, item_price=price, item_description=des, \
                           item_image="../../" + path[8:], item_seller_name="default", item_pickup_info="default")

@life.route('/request', methods=['POST', 'GET'])
# @check_login
def buy():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    requestForm = RequestForm()
    if request.method == 'POST':
        # print(requestForm.data)
        home = request.form.get('Home')
        create = request.form.get('create-request')
        cate = request.form.get('Category')
    
        title = requestForm.title.data
        info = requestForm.info.data

        # print(home, create, cate, title, info)

        if home == "Home": 
            return redirect(url_for('auth.logout'))
        if create == "create-request": 
            if cate == "": 
                return render_template('request.html', form=requestForm, itemCategories=CATEGORY, categoryInvalid=True)
            else: 
                requestdb.createRequest(current_user.email, title, cate, info)
                return redirect(url_for('life.home'))
                
    return render_template('request.html', form=requestForm, itemCategories=CATEGORY, categoryInvalid=False)

@life.route('/request/<requestID>', methods=['POST', 'GET'])
# @check_login
def requestList(requestID):    
    if requestID == "all":
        requestInfo = requestdb.getRequestList()
        return render_template('requestall.html', requestInfo=requestInfo)
    else:
        requestInfo = requestdb.findRequest(requestID)
        requestInfo["userName"] = accountdb.findUserName(requestInfo['requestUser'])
        if request.method == 'POST':
            sell = request.form.get('Sell')
            buy = request.form.get('Request')
            login = request.form.get('Login')
            signup = request.form.get('Signup')
            profile = request.form.get('Profile')

            # print(submit)
            if sell == "Sell": 
                return redirect(url_for('life.sell'))

            if buy == "Request": 
                return redirect(url_for('life.buy'))
            
            if login == "Login": 
                return redirect(url_for('auth.login'))
            
            if signup == "Signup": 
                return redirect(url_for('auth.signup'))

            if profile == "Profile": 
                return redirect(url_for('life.profile'))
            
        return render_template('requestdetail.html', requestInfo=requestInfo)

@life.route('/profile', methods=['POST', 'GET'])
# @check_login
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        logout = request.form.get('logout')

        if logout == "logout": 
            return redirect(url_for('auth.logout'))
        
    return render_template('profile.html')