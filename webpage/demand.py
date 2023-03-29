import os
from flask import Flask
from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, buttonCheck
from db import itemdb, requestdb, accountdb, chatdb

demand = Blueprint('demand',__name__)

@demand.route('/', methods=['POST', 'GET'])
def home():
    if current_user.is_authenticated: userStatus = True
    else: userStatus = False
    requestInfo = requestdb.getRequestList()
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button
    return render_template('demandall.html', requestInfo=requestInfo, userStatus=userStatus)


@demand.route('/<requestID>', methods=['POST', 'GET'])
# @check_login
def demanddetail(requestID):

    requestInfo = requestdb.findRequest(requestID)
    requestInfo["userName"] = accountdb.findUserName(requestInfo['requestUser'])
    if current_user.is_authenticated: userStatus = True
    else: userStatus = False

    myItem = myItemList = {}
    identity = ""
    if userStatus:
        if current_user.email == requestInfo["requestUser"]: identity = "owner"
        else: identity = "seller"
        myItem = itemdb.getItemList(user=current_user.email)
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
# @check_login
def demandcreate():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', addr=request.full_path))
    
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
                requestdb.createRequest(current_user.email, title, cate, info)
                return redirect(url_for('demand.home'))
                
    return render_template('demandcreate.html', form=requestForm, itemCategories=CATEGORY, categoryInvalid=False)

