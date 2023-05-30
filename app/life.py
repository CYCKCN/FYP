import os
from flask import Flask
from flask import Blueprint, request, session, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, buttonCheck
from db import itemdb, requestdb, accountdb, bargaindb

life = Blueprint('life',__name__)

@life.route('/login', methods=['POST', 'GET'])
def login():
    if "email" in session: 
        userStatus = True
        return redirect(url_for('market.home'))
    else: userStatus = False

    if request.method == 'POST':
        login_btn = request.form.get('Login')
        email = request.form.get('email')
        if login_btn == "Login": 
            session['email'] = email
            userStatus = True

            account = accountdb.findUser(session["email"])
            if not account: 
                accountdb.signup(session["email"])
                
            if 'oauth_origin' in session: 
                return redirect(session['oauth_origin'])
            else: 
                return redirect(url_for('market.home'))

    return render_template('login.html', userStatus=userStatus)

@life.route('/aboutus', methods=['POST', 'GET'])
def aboutus():
    return render_template('tree.html')

@life.route('/profile', methods=['POST', 'GET'])
def profile():
    if "email" not in session:
        session['oauth_origin'] = request.full_path
        return redirect(url_for('auth.google_login'))
    
    section = request.args.get('section')
    user = accountdb.findUser(session["email"])
    itemInfo = itemdb.getItemList(user=session["email"])
    requestInfo = requestdb.getRequestList(user=session["email"])
    # bargainList = bargaindb.findBargainList(session['email'])
    # bargainItemList = []
    # for bargain in bargainList:
    #     item = itemdb.findItem(bargain["bargainItem"])
    #     if item: bargainItemList.append(item)
    myReservedItem = itemdb.findMyReservedItem(session['email'])

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
        create = request.form.get("Create")
        if create == 'Create-item':
            return redirect(url_for('market.giveitem'))
        category = request.form.get("category")
        if category:
            return redirect(url_for("market.home", cate=category, search='', filter=''))
        
        # if itemID:
        #     item = itemdb.findItem(itemID)
        #     if session["email"] == item['itemOwner']:
        #         chat = chatdb.findChatByOwner(itemID, session["email"])
        #     else:
        #         chat = chatdb.findChatByBuyer(itemID, session["email"])
        #     return redirect(url_for('life.chat', chatID=chat["chatID"]))
        
    return render_template('profile.html', user=user, section=section if section else "Info", itemCategories=CATEGORY, itemInfo=itemInfo, requestInfo=requestInfo, myReservedItem=myReservedItem)

@life.route('/chat', methods=['POST', 'GET'])
def chat():
    filter = request.args.get('filter') if request.args.get('filter') else 'buyer'
    itemID = request.args.get('itemID')
    bargainName = request.args.get('bargainName')
    selected_bargain = None
    infoList = []
    # if not type:
    #     bargainList = bargaindb.findBargainList(session['email'])
    if filter == 'owner':
        myItemList = itemdb.getItemList(session['email'])
        for _, item in myItemList.items():
            bargainItemList = bargaindb.findBargainByItem(item['itemID'])
            for bargain in bargainItemList: 
                infoList.append((bargain, item))
        if bargainName: selected_bargain = bargaindb.findBargainByBuyer(bargainName.split(',')[0], bargainName.split(',')[1])
    else:
        bargainList = bargaindb.findBargainList(session['email'])
        for bargain in bargainList:
            item = itemdb.findItem(bargain['bargainItem'])
            infoList.append((bargain, item))
        if itemID: selected_bargain = bargaindb.findBargainByBuyer(itemID, session['email'])
        if bargainName: selected_bargain = bargaindb.findBargainByBuyer(bargainName.split(',')[0], session['email'])

    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button
        category = request.form.get("category")
        if category:
            return redirect(url_for("market.home", cate=category, search='', filter=''))
        type = request.form.get('type')
        if type:
            return(redirect(url_for('life.chat', filter=type, itemID=None, bargainName=None)))
        bargainID = request.form.get('bargainID')
        if bargainID:
            return(redirect(url_for('life.chat', filter=filter, itemID=None, bargainName=bargainID)))
        notes = request.form.get('search-keyword')
        submit = request.form.get('Send')
        if notes and submit and selected_bargain:
            bargaindb.sendNotes(selected_bargain, notes, session['email'])
            return(redirect(url_for('life.chat', filter=filter, itemID=itemID, bargainName=bargainName)))
        priceChange = request.form.get('raise-price')
        priceChangeBtn = request.form.get('price-btn')
        if priceChange and priceChangeBtn and selected_bargain:
            bargaindb.changePrice(selected_bargain, priceChange)
            return(redirect(url_for('life.chat', filter=filter, itemID=itemID, bargainName=bargainName)))
        acceptBtn = request.form.get('accept-btn')
        if acceptBtn and selected_bargain:
            if acceptBtn == "Accept": 
                itemdb.reserveItem(selected_bargain["bargainItem"], selected_bargain['bargainFrom'])
                bargaindb.agreePrice(selected_bargain)
            else: bargaindb.declinePrice(selected_bargain)
            return(redirect(url_for('life.chat', filter=filter, itemID=itemID, bargainName=bargainName)))
        create = request.form.get("Create")
        if create == 'Create-item':
            return redirect(url_for('market.giveitem'))
    # print(selected_bargain)
    return render_template('chat.html', userName=session['email'], selected_bargain=selected_bargain, selected_type=filter, infoList=infoList, itemCategories=CATEGORY)

# @life.route('/demand/<requestID>', methods=['POST', 'GET'])
# def demanddetail(requestID):
#     requestInfo = requestdb.findRequest(requestID)
#     requestInfo["userName"] = accountdb.findUserName(requestInfo['requestUser'])
#     if "email" in session: userStatus = True
#     else: userStatus = False

#     myItem = myItemList = {}
#     identity = ""
#     if userStatus:
#         if session["email"] == requestInfo["requestUser"]: identity = "owner"
#         else: identity = "seller"
#         myItem = itemdb.getItemList(user=session["email"])
#         for k, v in myItem.items():
#             if v not in requestInfo["requestItemList"]:
#                 myItemList[k] = v
#     if request.method == 'POST':
#         button = buttonCheck(request.form)
#         if button: return button
#         submit = request.form.get('submit')
#         itemID = request.form.get('selectedItem')
#         deal = request.form.get('deal')
#         decline = request.form.get('decline')
#         if submit and itemID:
#             requestdb.addRequestItemList(requestID, itemID)
#             return redirect(url_for('demand.demanddetail', requestID=requestID))

#         if deal:
#             requestdb.dealRequestItem(requestID, deal)
#             return redirect(url_for('demand.demanddetail', requestID=requestID))

#         if decline:
#             requestdb.declineRequestItem(requestID, decline)
#             return redirect(url_for('demand.demanddetail', requestID=requestID))
        
#     # print(userStatus, identity, sold)
#     return render_template('demanddetail.html', requestInfo=requestInfo, userStatus=userStatus, identity=identity, itemList=requestInfo["requestItemList"], myItemList=myItemList)