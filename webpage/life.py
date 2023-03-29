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
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button

        market = request.form.get('market')
        plazza = request.form.get('plazza')
        demand = request.form.get('demand')

        if market == "market": 
            return redirect(url_for('market.home'))
        
        if plazza == "plazza": 
            return redirect(url_for('plazza.home'))
        
        if demand == "demand": 
            return redirect(url_for('demand.home'))
        
    return render_template('home.html')

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
