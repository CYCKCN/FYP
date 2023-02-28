import os
from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from .auth import check_login

from utils import User, allowed_file, UPLOAD_FOLDER
from db import itemdb

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
    if request.method == 'POST':
        home = request.form.get('Home')
        submit = request.form.get('create-contract')
        name = request.form.get('Name')
        price = request.form.get('Price')
        category = request.form.get('Category')
        info = request.form.get('Description')
        print(request.files)
        if "upload_cont_img" in request.files: file = request.files['upload_cont_img']
        else: file = None
        image_path = ""

        print(name, price, category, info)
        print(submit)

        if home == "Home": 
            return redirect(url_for('life.home'))
        
        if file and file.filename != "" and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = os.path.join(UPLOAD_FOLDER, filename)
        print(image_path)
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
        if home == "Home": 
            return redirect(url_for('life.home'))

    return render_template('item.html', item_name=name, item_category=cate, item_price=price, item_description=des, \
                           item_image="../../" + path[8:], item_seller_name="default", item_pickup_info="default")