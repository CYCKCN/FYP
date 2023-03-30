import os
from flask import Flask
from flask import Blueprint, request, session, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, buttonCheck
from db import itemdb, requestdb, accountdb, chatdb

life = Blueprint('life',__name__)

@life.route('/', methods=['POST', 'GET'])
def home():
    if "email" in session: userStatus = True
    else: userStatus = False

    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button

        market = request.form.get('market')
        piazza = request.form.get('piazza')
        demand = request.form.get('demand')

        if market == "market": 
            return redirect(url_for('market.home'))
        
        if piazza == "piazza": 
            return redirect(url_for('piazza.home'))
        
        if demand == "demand": 
            return redirect(url_for('demand.home'))
        
    return render_template('home.html', userStatus=userStatus)

@life.route('/profile', methods=['POST', 'GET'])
def profile():
    if "email" not in session:
        return redirect(url_for('auth.login', addr=request.full_path))
    
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

@life.route('/chat/<chatID>', methods=['POST', 'GET'])
def chat(chatID):
    if "email" not in session:
        return redirect(url_for('auth.login', addr=request.full_path))
    
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
