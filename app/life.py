import os
from flask import Flask
from flask import Blueprint, request, session, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, buttonCheck
from db import itemdb, requestdb, accountdb, chatdb

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
    chatInfo = chatdb.getChatList(user=session["email"])

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
            if session["email"] == item['itemOwner']:
                chat = chatdb.findChatByOwner(itemID, session["email"])
            else:
                chat = chatdb.findChatByBuyer(itemID, session["email"])
            return redirect(url_for('life.chat', chatID=chat["chatID"]))
        
    return render_template('profile.html', user=user, section=section if section else "Info", itemInfo=itemInfo, requestInfo=requestInfo, chatInfo=chatInfo)

@life.route('/demand/<requestID>', methods=['POST', 'GET'])
def demanddetail(requestID):
    requestInfo = requestdb.findRequest(requestID)
    requestInfo["userName"] = accountdb.findUserName(requestInfo['requestUser'])
    if "email" in session: userStatus = True
    else: userStatus = False

    myItem = myItemList = {}
    identity = ""
    if userStatus:
        if session["email"] == requestInfo["requestUser"]: identity = "owner"
        else: identity = "seller"
        myItem = itemdb.getItemList(user=session["email"])
        for k, v in myItem.items():
            if v not in requestInfo["requestItemList"]:
                myItemList[k] = v
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button
        submit = request.form.get('submit')
        itemID = request.form.get('selectedItem')
        deal = request.form.get('deal')
        decline = request.form.get('decline')
        if submit and itemID:
            requestdb.addRequestItemList(requestID, itemID)
            return redirect(url_for('demand.demanddetail', requestID=requestID))

        if deal:
            requestdb.dealRequestItem(requestID, deal)
            return redirect(url_for('demand.demanddetail', requestID=requestID))

        if decline:
            requestdb.declineRequestItem(requestID, decline)
            return redirect(url_for('demand.demanddetail', requestID=requestID))
        
    # print(userStatus, identity, sold)
    return render_template('demanddetail.html', requestInfo=requestInfo, userStatus=userStatus, identity=identity, itemList=requestInfo["requestItemList"], myItemList=myItemList)

@life.route('/item/<itemID>', methods=['POST', 'GET'])
def item(itemID):
    item = itemdb.findItem(itemID)
    if "email" in session: userStatus = True
    else: userStatus = False

    if not item:
        return "Record not found", 400
    
    if userStatus and item["itemOwner"] == session["email"]:
        return redirect(url_for('market.itemManager', itemID=itemID))
    
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button

        reserve = request.form.get('Reserve')
        if reserve == "Reserve":
            if userStatus:
                itemdb.reserveItem(itemID, session["email"])
                item = itemdb.findItem(itemID)
                return render_template('item.html', item=item, userStatus=userStatus)
            else:
                session['oauth_origin'] = request.full_path
                return redirect(url_for('auth.google_login'))
        
        contact = request.form.get('Contact')
        if contact == "Contact":
            if userStatus:
                chat = chatdb.findChatByBuyer(itemID, session["email"])
                # print(chat)
                if not chat:
                    # print("no chat")
                    chat = chatdb.createChat(itemID, session["email"])
                return redirect(url_for('life.chat', chatID=chat["chatID"]))
            else:
                session['oauth_origin'] = request.full_path
                return redirect(url_for('auth.google_login'))

    return render_template('item.html', item=item, userStatus=userStatus)

@life.route('/itemManager/<itemID>', methods=['POST', 'GET'])
def itemManager(itemID):
    if "email" not in session:
        session['oauth_origin'] = request.full_path
        return redirect(url_for('auth.google_login'))
    
    item = itemdb.findItem(itemID)
    if not item:
        return "Record not found", 400
    
    if item["itemOwner"] != session["email"]:
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

@life.route('/chat/<chatID>', methods=['POST', 'GET'])
def chat(chatID):
    if "email" not in session:
        session['oauth_origin'] = request.full_path
        return redirect(url_for('auth.google_login'))
    

    chat = chatdb.findChatByID(chatID)
    item = itemdb.findItem(chat["chatItem"])
    chat["sendBy"] = session["email"]
    if chat["chatBuyer"] == session["email"]:
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