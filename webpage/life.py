import os
from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER
from db import itemdb

life = Blueprint('life',__name__)

@life.route('/home', methods=['POST', 'GET'])
def home():
    
    itemList = itemdb.getItemList()
    itemInfo = {}
    counter = 0
    for item in itemList:
        itemInfo[str(counter)] = item
        itemInfo[str(counter)]['itemImg'] = "../../" + itemInfo[str(counter)]['itemImg'][8:]
        counter += 1
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

    return render_template('home.html', itemInfo=itemInfo, userStatus=userStatus)

@life.route('/sell', methods=['POST', 'GET'])
# @check_login
def sell():
    if request.method == 'POST':
        home = request.form.get('Home')
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
    return render_template('request.html')

@life.route('/profile', methods=['POST', 'GET'])
# @check_login
def profile():
    if request.method == 'POST':
        logout = request.form.get('create-contract')

        if logout == "create-contract": 
            return redirect(url_for('auth.logout'))
        
    return render_template('profile.html')