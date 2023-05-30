import os
from flask import Flask
from flask import Blueprint, request, session, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, CONDITION, PRICERANGE, RequestForm, ItemForm, buttonCheck#, ds_client, gcs_client, BUCKET
from db import itemdb, requestdb, accountdb, chatdb, bargaindb

# from google.cloud import exceptions, ndb, storage

market = Blueprint('market',__name__)

@market.route('/', methods=['POST', 'GET'])
def home():
    if "email" in session: userStatus = True
    else: 
        userStatus = False
        session['oauth_origin'] = request.full_path
        return redirect(url_for('life.login'))

    cate = request.args.get('cate')
    # maxprice = request.args.get('maxprice')
    # minprice = request.args.get('minprice')
    search = request.args.get('search')
    filter = request.args.get('filter')

    # print(cate, maxprice, minprice, search)
    # print(filter)
    itemInfo = itemdb.getItemList(cate=cate if cate in CATEGORY else "", search=search if search else "", filter=filter if filter and filter != "All" else "")

    # if (maxprice, minprice) == ('50', '0'): price = 'Less than 50'
    # elif (maxprice, minprice) == ('100', '50'): price = 'Between 50 - 100'
    # elif (maxprice, minprice) == ('200', '100'): price = 'Between 100 - 200'
    # elif (maxprice, minprice) == ('', '200'): price = 'More than 200'
    # else: price = ""

    requestInfo = requestdb.getRequestList(noSold=True)
    # print(requestInfo)

    if request.method == 'POST':
        
        button = buttonCheck(request.form)
        if button: return button

        category = request.form.get("category")
        # print(cate)
        # price = request.form.get("Price")
        create = request.form.get("Create")
        itemName = request.form.get("search-keyword")
        apply = request.form.get("Apply")
        section = request.form.get('section-btn')
        
        # demand = request.form.get("Demand")
        if itemName == '' and search != '': itemName = search
        # itemName = searchForm.search.data

        # if price == 'Less than 50': maxprice, minprice = '50', '0'
        # elif price == 'Between 50 - 100': maxprice, minprice = '100', '50'
        # elif price == 'Between 100 - 200': maxprice, minprice = '200', '100'
        # elif price == 'More than 200': maxprice, minprice = '', '200'
        # else: maxprice, minprice = '', ''

        # print(cate, maxprice, minprice, itemName)

        # if demand == 'Demand':
        #     return redirect(url_for('life.demand'))

        # if clear == 'Clear':
        #     return redirect(url_for("market.home", cate='', maxprice='', minprice='', search=''))
        
        # if apply == "Apply" or itemName:
        #     return redirect(url_for("market.home", cate=cate, maxprice=maxprice, minprice=minprice, search=itemName))

        if category:
            return redirect(url_for("market.home", cate=category, search='', filter=''))
        
        if itemName and apply:
            return redirect(url_for("market.home", cate=cate, search=itemName, filter=filter))

        if create == 'Create-item':
            return redirect(url_for('market.giveitem'))
        # if create == 'Create-request':
        #     return redirect(url_for('demand.demandcreate'))

        if section:
            return redirect(url_for("market.home", filter=section, cate=cate, search=''))
        
        requestBtn = request.form.get('request-send')
        requestCtx = request.form.get('request-congtent')
        
        if requestBtn and requestCtx:
            requestdb.createRequest(session['email'], requestCtx)
            return redirect(url_for("market.home", cate=cate, search=""))

    # print(price)
    return render_template('market.html', userName=session['email'], search=search if search else 'Search Now', selected_cate=cate if cate else '', selected_section=filter if filter else 'All', itemInfo=itemInfo, requestInfo=requestInfo, userStatus=userStatus, itemCategories=CATEGORY, itemCondition=CONDITION)

@market.route('/giveitem', methods=['POST', 'GET'])
def giveitem():
    if "email" not in session:
        session['oauth_origin'] = request.full_path
        return redirect(url_for('auth.google_login'))
    
    itemImg = ""
    itemForm = ItemForm()
    invalidDict = {"name": False, "cate": False, "cond": False, "price": False, "info": False, "pickup": False,  "img": False}

    if request.method == 'POST':
        submit = request.form.get('create-contract')
        category = request.form.get('Category')
        condition = request.form.get('Condition')
        free = request.form.get('Free')
        market = request.form.get('market')

        name = itemForm.name.data
        price = 0 if free else itemForm.price.data
        info = itemForm.description.data
        pickup = itemForm.pickup.data

        # print(name, price, info, pickup)
        
        if "upload_cont_img" in request.files: file = request.files['upload_cont_img']
        else: file = None
        image_path = ""

        button = buttonCheck(request.form)
        if button: return button
        # print(market)
        if market:
            return redirect(url_for("market.home", cate=market, search='', filter=''))
        
        # print(image_path)
        if submit == "new-contract":
            if file and file.filename != "" and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # blob = gcs_client.bucket(BUCKET).blob(filename)
                # blob.upload_from_file(file, content_type=file.content_type)
                image_path = filename
                # file.save(os.path.join(os.getcwd(), UPLOAD_FOLDER, filename))
                # image_path = os.path.join(UPLOAD_FOLDER, filename)
                # itemImg = "../../" + image_path[4:]
                # print(os.path.join(os.getcwd(), UPLOAD_FOLDER, filename))
            else: invalidDict["img"] = True

            if not name: invalidDict["name"] = True
            if category == "": invalidDict["cate"] = True 
            if condition == "": invalidDict["cond"] = True 
            if not free and not price: invalidDict["price"] = True
            if not info: invalidDict["info"] = True
            if not pickup: invalidDict["pickup"] = True
            if True in invalidDict.values():
                return render_template('giveitem.html', form=itemForm, itemCategories=CATEGORY, invalidDict=invalidDict)
            
            itemdb.createItem(session["email"], name, price, category, condition, info, image_path, pickup)
            return redirect(url_for('market.home'))
    return render_template('giveitem.html', userName=session['email'], form=itemForm, itemCategories=CATEGORY, itemCondition=CONDITION, invalidDict=invalidDict)
    # return "Sell Page"

@market.route('/item/<itemID>', methods=['POST', 'GET'])
def item(itemID):
    item = itemdb.findItem(itemID)
    if "email" in session: userStatus = True
    else: 
        userStatus = False
        session['oauth_origin'] = request.full_path
        return redirect(url_for('life.login'))

    if not item:
        return "Record not found", 400
    
    if userStatus and item["itemOwner"] == session["email"]:
        return redirect(url_for('market.itemManager', itemID=itemID))
    
    bargain = bargaindb.findBargainByBuyer(itemID, session['email'])
    if bargain: bargaindb.checkTime(bargain)
    
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button

        category = request.form.get("category")
        if category:
            return redirect(url_for("market.home", cate=category, search=''))
        
        reserve = request.form.get('Reserve')
        if reserve == "Reserve":
            if userStatus:
                itemdb.reserveItem(itemID, session["email"])
                item = itemdb.findItem(itemID)
                return render_template('item.html', item=item, userStatus=userStatus)
            else:
                session['oauth_origin'] = request.full_path
                return redirect(url_for('life.login'))
        
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
                return redirect(url_for('life.login'))
        
        price = request.form.get('user-price')
        notes = request.form.get('user-notes')
        submit = request.form.get('submit')
        # print(price, notes, submit)
        if submit == "submit" and price:
            # print(price, notes, submit)
            bargain = bargaindb.findBargainByBuyer(itemID, session['email'])
            if not bargain:
                bargaindb.createBargain(itemID, session['email'])
            bargaindb.sendBargain(itemID, session['email'], session['email'], price, notes)
            return redirect(url_for('market.item', itemID=itemID))
                
    return render_template('item.html', item=item, itemCategories=CATEGORY, userStatus=userStatus, bargainInfo=bargain["bargainInfo"] if bargain else [], bargainBuyer=session['email'])

@market.route('/itemManager/<itemID>', methods=['POST', 'GET'])
def itemManager(itemID):
    if "email" not in session:
        session['oauth_origin'] = request.full_path
        return redirect(url_for('life.login'))
    
    item = itemdb.findItem(itemID)
    if not item:
        return "Record not found", 400
    
    if item["itemOwner"] != session["email"]:
        return "No Acess", 400
    
    bargainUserList = []
    bargainInfo = []
    bargainList = bargaindb.findBargainByItem(itemID)
    for bargain in bargainList: 
        bargaindb.checkTime(bargain)
        bargainUserList.append(bargain["bargainFrom"])

    user = request.args.get('user')
    if user:
        bargainUser = bargaindb.findBargainByBuyer(itemID, user)
        bargainInfo = bargainUser["bargainInfo"]
    elif bargainUserList: 
        user = bargainUserList[0]
        bargainUser = bargaindb.findBargainByBuyer(itemID, user)
        bargainInfo = bargainUser["bargainInfo"]
    print(user)
    # print(bargainInfo)
    if request.method == 'POST':
        button = buttonCheck(request.form)
        if button: return button

        deal = request.form.get('deal')
        deny = request.form.get('decline')
        delete = request.form.get('item-delete')

        if deal == "deal":
            itemdb.dealItem(itemID)
        
        if deny == "decline":
            itemdb.denyItem(itemID)

        if delete == "item-delete":
            itemdb.deleteItem(itemID)
            return redirect(url_for('market.home'))
        
        section = request.form.get('section')
        if section:
            return redirect(url_for('market.itemManager', itemID=itemID, user=section))
        
        selectedItem = request.form.get('selectedItem')
        ownerNotes = request.form.get('owner-notes')
        agree = request.form.get('agree')
        decline = request.form.get('decline')
        if selectedItem and ownerNotes and (agree or decline):
            if agree: itemdb.reserveItem(itemID, user)
            bargaindb.replyBargain(itemID, user, session['email'], agree if agree else decline, ownerNotes, int(selectedItem))
            return redirect(url_for('market.itemManager', itemID=itemID, user=user))
        
    return render_template('itemmanage.html', item=item, bargainUserList=bargainUserList, bargainInfo=bargainInfo, bargainBuyer=user)

