import os
from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, RequestForm, buttonCheck
from db import itemdb, requestdb, accountdb

life = Blueprint('life',__name__)

@life.route('/home', methods=['POST', 'GET'])
def home():
    if current_user.is_authenticated: userStatus = True
    else: userStatus = False

    cate = request.args.get('cate')
    maxprice = request.args.get('maxprice')
    minprice = request.args.get('minprice')
    # print(cate, maxprice, minprice)
    itemInfo = itemdb.getItemList(cate if cate else "", maxprice if maxprice else "", minprice if minprice else "")

    requestInfo = requestdb.getRequestList()

    if request.method == 'POST':
        
        button = buttonCheck(request.form)
        if button: return button

        apply = request.form.get('Apply')
        cate = request.form.get("Category")
        price = request.form.get("Price")

        if price == 'Less than 50': maxprice, minprice = '50', '0'
        elif price == 'Between 50 - 100': maxprice, minprice = '100', '50'
        elif price == 'Between 100 - 200': maxprice, minprice = '200', '100'
        elif price == 'More than 200': maxprice, minprice = '', '200'
        else: maxprice, minprice = '', ''

        print(cate, maxprice, minprice)

        if apply: return redirect(url_for("life.home", cate=cate, maxprice=maxprice, minprice=minprice))

    return render_template('home.html', selected=cate if cate else '', itemInfo=itemInfo, requestInfo=requestInfo, userStatus=userStatus, itemCategories=CATEGORY)

@life.route('/sell', methods=['POST', 'GET'])
# @check_login
def sell():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
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

        button = buttonCheck(request.form)
        if button: return button
        
        if file and file.filename != "" and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = os.path.join(UPLOAD_FOLDER, filename)
        # print(image_path)
        if submit == "new-contract":
            itemdb.createItem(current_user.email, name, price, category, info, image_path)
            return redirect(url_for('life.home'))

    return render_template('sell.html', itemCategories=CATEGORY)
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

        button = buttonCheck(request.form)
        if button: return button

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
        create = request.form.get('create-request')
        cate = request.form.get('Category')
    
        title = requestForm.title.data
        info = requestForm.info.data

        # print(home, create, cate, title, info)

        button = buttonCheck(request.form)
        if button: return button

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
        if current_user.is_authenticated: userStatus = True
        else: userStatus = False

        if request.method == 'POST':
            button = buttonCheck(request.form)
            if button: return button
            
        return render_template('requestdetail.html', requestInfo=requestInfo, userStatus=userStatus)

@life.route('/profile', methods=['POST', 'GET'])
# @check_login
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    user = accountdb.findUser(current_user.email)
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button
        logout = request.form.get('logout')

        if logout == "logout": 
            return redirect(url_for('auth.logout'))
        
    return render_template('profile.html', user=user)