import os
from flask import Flask
from flask import Blueprint, request, session, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, buttonCheck
from db import itemdb, requestdb, accountdb, chatdb

demand = Blueprint('demand',__name__)

@demand.route('/', methods=['POST', 'GET'])
def home():
    if "email" in session: userStatus = True
    else: userStatus = False
    requestInfo = requestdb.getRequestList()
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button
        create = request.form.get("Create")
        if create == 'Create':
            return redirect(url_for('demand.demandcreate'))
    return render_template('demandall.html', requestInfo=requestInfo, userStatus=userStatus)


@demand.route('/<requestID>', methods=['POST', 'GET'])
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

@demand.route('/demandcreate', methods=['POST', 'GET'])
def demandcreate():
    if "email" not in session:
        session['oauth_origin'] = request.full_path
        return redirect(url_for('auth.google_login'))
    
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
                return render_template('demandcreate.html', form=requestForm, itemCategories=CATEGORY, categoryInvalid=True)
            else: 
                requestdb.createRequest(session["email"], title, cate, info)
                return redirect(url_for('demand.home'))
                
    return render_template('demandcreate.html', form=requestForm, itemCategories=CATEGORY, categoryInvalid=False)

@demand.route('/item/<itemID>', methods=['POST', 'GET'])
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

@demand.route('/itemManager/<itemID>', methods=['POST', 'GET'])
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