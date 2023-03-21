import os
from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, buttonCheck
from db import itemdb, requestdb, accountdb, chatdb

life = Blueprint('life',__name__)

@life.route('/', methods=['POST', 'GET'])
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
            return redirect(url_for("lifeverse.home", cate='', maxprice='', minprice='', search=''))

        if apply == "Apply" or itemName:
            return redirect(url_for("lifeverse.home", cate=cate, maxprice=maxprice, minprice=minprice, search=itemName))      

    # print(price)
    return render_template('home.html', search=search if search else 'Search Now', selected_cate=cate if cate else '', selected_price=price if price else '', itemInfo=itemInfo, requestInfo=requestInfo, userStatus=userStatus, itemCategories=CATEGORY, priceRange=PRICERANGE)

    # return render_template('home.html')

@life.route('/profile', methods=['POST', 'GET'])
# @check_login
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    section = request.args.get('section')
    user = accountdb.findUser(current_user.email)
    itemInfo = itemdb.getItemList(user=current_user.email)
    requestInfo = requestdb.getRequestList(user=current_user.email)
    chatInfo = chatdb.getChatList(user=current_user.email)

    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button
        section = request.form.get('section')
        logout = request.form.get('logout')
        itemID = request.form.get('item')

        if logout == "logout": 
            return redirect(url_for('auth.logout'))
        
        if section:
            return redirect(url_for('life.profile', section=section))
        
        if itemID:
            item = itemdb.findItem(itemID)
            if current_user.email == item['itemOwner']:
                chat = chatdb.findChatByOwner(itemID, current_user.email)
            else:
                chat = chatdb.findChatByBuyer(itemID, current_user.email)
            return redirect(url_for('life.chat', chatID=chat["chatID"]))
        
    return render_template('profile.html', user=user, section=section if section else "Info", itemInfo=itemInfo, requestInfo=requestInfo, chatInfo=chatInfo)

@life.route('/chat/<chatID>', methods=['POST', 'GET'])
# @check_login
def chat(chatID):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    chat = chatdb.findChatByID(chatID)
    item = itemdb.findItem(chat["chatItem"])
    chat["sendBy"] = current_user.email
    if chat["chatBuyer"] == current_user.email:
        chat["sendTo"] = accountdb.findUserName(item["itemOwner"])
        status = "buyer"
    else:
        chat["sendTo"] = accountdb.findUserName(chat["chatBuyer"])
        status = "owner"

    if request.method == 'POST':

        button = buttonCheck(request.form)
        if button: return button

        sendTxt = request.form.get("send-text")
        sendBtn = request.form.get("send-btn")

        if sendBtn == 'Send' and sendTxt:
            chatdb.sendChat(item["itemID"], chat["chatBuyer"], item["itemOwner"], sendTxt, status)
            return redirect(url_for('life.chat', chatID=chatID))
        
    return render_template('chat.html', item=item, chat=chat)
