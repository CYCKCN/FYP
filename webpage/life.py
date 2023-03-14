import os
from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, buttonCheck
from db import itemdb, requestdb, accountdb

life = Blueprint('life',__name__)

@life.route('/home', methods=['POST', 'GET'])
def home():
    if current_user.is_authenticated: userStatus = True
    else: userStatus = False

    cate = request.args.get('cate')
    maxprice = request.args.get('maxprice')
    minprice = request.args.get('minprice')
    search = request.args.get('search')

    # print(cate, maxprice, minprice, search)
    itemInfo = itemdb.getItemList(cate=cate if cate else "", maxprice=maxprice if maxprice else "", \
                                  minprice=minprice if minprice else "", search=search if search else "")

    if (maxprice, minprice) == ('50', '0'): price = 'Less than 50'
    elif (maxprice, minprice) == ('100', '50'): price = 'Between 50 - 100'
    elif (maxprice, minprice) == ('200', '100'): price = 'Between 100 - 200'
    elif (maxprice, minprice) == ('', '200'): price = 'More than 200'
    else: price = ""

    requestInfo = requestdb.getRequestList()
    # print(requestInfo)

    if request.method == 'POST':
        
        button = buttonCheck(request.form)
        if button: return button

        apply = request.form.get('Apply')
        clear = request.form.get('Clear')
        cate = request.form.get("Category")
        price = request.form.get("Price")
        itemName = request.form.get("search-keyword")
        if itemName == '' and search != '': itemName = search
        # itemName = searchForm.search.data

        if price == 'Less than 50': maxprice, minprice = '50', '0'
        elif price == 'Between 50 - 100': maxprice, minprice = '100', '50'
        elif price == 'Between 100 - 200': maxprice, minprice = '200', '100'
        elif price == 'More than 200': maxprice, minprice = '', '200'
        else: maxprice, minprice = '', ''

        # print(cate, maxprice, minprice, itemName)

        if clear == 'Clear':
            return redirect(url_for("life.home", cate='', maxprice='', minprice='', search=''))

        if apply == "Apply" or itemName:
            return redirect(url_for("life.home", cate=cate, maxprice=maxprice, minprice=minprice, search=itemName))      

    # print(price)
    return render_template('home.html', search=search if search else 'Search Now', selected_cate=cate if cate else '', selected_price=price if price else '', itemInfo=itemInfo, requestInfo=requestInfo, userStatus=userStatus, itemCategories=CATEGORY, priceRange=PRICERANGE)

@life.route('/sell', methods=['POST', 'GET'])
# @check_login
def sell():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    selected_cate = ""
    itemImg = ""
    itemForm = ItemForm()
    invalidDict = {"name": False, "price": False, "info": False, "pickup": False, "cate": False, "img": False}
    if request.method == 'POST':
        submit = request.form.get('create-contract')
        selected_cate = category = request.form.get('Category')

        name = itemForm.name.data
        price = itemForm.price.data
        info = itemForm.description.data
        pickup = itemForm.pickup.data

        print(name, price, info, pickup)
        
        if "upload_cont_img" in request.files: file = request.files['upload_cont_img']
        else: file = None
        image_path = ""

        button = buttonCheck(request.form)
        if button: return button
        
        if file and file.filename != "" and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            itemImg = image_path
        else: invalidDict["img"] = True
        if category == "": invalidDict["cate"] = True
        if not name: invalidDict["name"] = True
        if not price: invalidDict["price"] = True
        if not info: invalidDict["info"] = True
        if not pickup: invalidDict["pickup"] = True
        print(invalidDict)
        if True in invalidDict.values():
            return render_template('sell.html', form=itemForm, itemCategories=CATEGORY, invalidDict=invalidDict)
        # print(image_path)
        if submit == "new-contract":
            itemdb.createItem(current_user.email, name, price, category, info, image_path, pickup)
            return redirect(url_for('life.home'))

    return render_template('sell.html', form=itemForm, itemCategories=CATEGORY, invalidDict=invalidDict, itemImg=itemImg, selected_cate=selected_cate)
    # return "Sell Page"

@life.route('/item/<itemID>', methods=['POST', 'GET'])
# @check_login
def item(itemID):
    item = itemdb.findItem(itemID)
    if not item:
        return "Record not found", 400
    
    if item["itemOwner"] == current_user.email:
        return redirect(url_for('life.itemManager', itemID=itemID))
    
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button

        reserve = request.form.get('Reserve')
        if reserve == "Reserve":
            itemdb.reserveItem(itemID, current_user.email)
            item = itemdb.findItem(itemID)
            return render_template('item.html', item=item)

    return render_template('item.html', item=item)

@life.route('/itemManager/<itemID>', methods=['POST', 'GET'])
# @check_login
def itemManager(itemID):
    item = itemdb.findItem(itemID)
    if not item:
        return "Record not found", 400
    
    if item["itemOwner"] != current_user.email:
        return "No Acess", 400
    
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button

        deal = request.form.get('deal')
        deny = request.form.get('decline')

        if deal == "deal":
            itemdb.dealItem(itemID)
        
        if deny == "decline":
            itemdb.denyItem(itemID)
        
    return render_template('itemmanage.html', item=item)

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
        if request.method == 'POST':
            button = buttonCheck(request.form)
            if button: return button
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
    section = request.args.get('section')
    user = accountdb.findUser(current_user.email)
    itemInfo = itemdb.getItemList(user=current_user.email)
    requestInfo = requestdb.getRequestList(user=current_user.email)

    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button
        section = request.form.get('section')
        logout = request.form.get('logout')

        if logout == "logout": 
            return redirect(url_for('auth.logout'))
        
        if section:
            return redirect(url_for('life.profile', section=section))
        
    return render_template('profile.html', user=user, section=section if section else "Info", itemInfo=itemInfo, requestInfo=requestInfo)

@life.route('/chat', methods=['POST', 'GET'])
# @check_login
def chat():
    return render_template('chat.html')

