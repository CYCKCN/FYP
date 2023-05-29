import os
from flask import Flask
from flask import Blueprint, request, session, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from utils import User, allowed_file, UPLOAD_FOLDER, CATEGORY, PRICERANGE, RequestForm, ItemForm, buttonCheck
from db import itemdb, requestdb, accountdb, chatdb, bargaindb

market = Blueprint('market',__name__)

@market.route('/', methods=['POST', 'GET'])
def home():
    if "email" in session: userStatus = True
    else: 
        userStatus = False
        session['oauth_origin'] = request.full_path
        return redirect(url_for('life.login'))

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
        create = request.form.get("Create")
        itemName = request.form.get("search-keyword")

        # demand = request.form.get("Demand")
        if itemName == '' and search != '': itemName = search
        # itemName = searchForm.search.data

        if price == 'Less than 50': maxprice, minprice = '50', '0'
        elif price == 'Between 50 - 100': maxprice, minprice = '100', '50'
        elif price == 'Between 100 - 200': maxprice, minprice = '200', '100'
        elif price == 'More than 200': maxprice, minprice = '', '200'
        else: maxprice, minprice = '', ''

        # print(cate, maxprice, minprice, itemName)

        # if demand == 'Demand':
        #     return redirect(url_for('life.demand'))

        if clear == 'Clear':
            return redirect(url_for("market.home", cate='', maxprice='', minprice='', search=''))
        
        if apply == "Apply" or itemName:
            return redirect(url_for("market.home", cate=cate, maxprice=maxprice, minprice=minprice, search=itemName))

        if create == 'Create-item':
            return redirect(url_for('market.giveitem'))
        if create == 'Create-request':
            return redirect(url_for('demand.demandcreate'))
        
        requestBtn = request.form.get('request-send')
        requestCtx = request.form.get('request-congtent')
        
        if requestBtn and requestCtx:
            requestdb.createRequest(session['email'], requestCtx)
            return redirect(url_for("market.home", cate=cate, maxprice=maxprice, minprice=minprice, search=itemName))

    # print(price)
    return render_template('market.html', search=search if search else 'Search Now', selected_cate=cate if cate else '', selected_price=price if price else '', itemInfo=itemInfo, requestInfo=requestInfo, userStatus=userStatus, itemCategories=CATEGORY, priceRange=PRICERANGE)

@market.route('/giveitem', methods=['POST', 'GET'])
def giveitem():
    if "email" not in session:
        session['oauth_origin'] = request.full_path
        return redirect(url_for('auth.google_login'))
    
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
            itemImg = "../../" + image_path[4:]
        else: invalidDict["img"] = True
        print(itemImg)
        if category == "": invalidDict["cate"] = True
        if not name: invalidDict["name"] = True
        if not price: invalidDict["price"] = True
        if not info: invalidDict["info"] = True
        if not pickup: invalidDict["pickup"] = True
        print(itemImg)
        if True in invalidDict.values():
            return render_template('giveitem.html', form=itemForm, itemCategories=CATEGORY, invalidDict=invalidDict)
        # print(image_path)
        if submit == "new-contract":
            itemdb.createItem(session["email"], name, price, category, info, image_path, pickup)
            return redirect(url_for('market.home'))

    return render_template('giveitem.html', form=itemForm, itemCategories=CATEGORY, invalidDict=invalidDict, itemImg=itemImg, selected_cate=selected_cate)
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
                
    return render_template('item.html', item=item, userStatus=userStatus, bargainInfo=bargain["bargainInfo"] if bargain else [])

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
            bargaindb.replyBargain(itemID, user, session['email'], agree if agree else decline, ownerNotes, int(selectedItem))
            return redirect(url_for('market.itemManager', itemID=itemID, user=user))
        
    return render_template('itemmanage.html', item=item, bargainUserList=bargainUserList, bargainInfo=bargainInfo)

