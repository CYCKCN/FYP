
from pymongo.mongo_client import MongoClient
from utils import Account, User, Item, Request, Chat, Story, Bargain, randomID, IDLENGTH, UNIADDR

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
    
def connection(dbname):
    addr = "mongodb+srv://admin:admin@life2.dwrako7.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(addr)
    db = client[dbname]
    return db

class AccountDB():
    def __init__(self, db):
        self.db = db["account"]
    
    def cleardb(self):
        self.db.delete_many({})

    def findUser(self, accountEmail):
        return self.db.find_one({"accountEmail": accountEmail})
    
    # def findUserName(self, accountEmail):
    #     account = self.db.find_one({"accountEmail": accountEmail})
    #     if account is None: return "Err: Not Registered!"
    #     return account["accountName"]
    
    # def login(self, accountEmail, accountPw):
    #     account = self.db.find_one({"accountEmail": accountEmail})
    #     if account is None: 
    #         return "Err: Not Registered!"
    #     elif check_password_hash(account["accountPw"], accountPw) == False:
    #         return "Err: Wrong Password!"
    #     else:
    #         return "Info: Login successfully!"
        
    def signup(self, accountEmail):
        # print(accountName, accountPw, accountEmail, accountUni)
        if self.db.find_one({"accountEmail": accountEmail}):
            return "Err: Account Exists!"
        newAccount = Account(accountEmail)
        self.db.insert_one(newAccount.__dict__)
        return "Info: Register USER Account Successfully"

class ItemDB():
    def __init__(self, db):
        self.db = db["item"]

    def cleardb(self):
        self.db.delete_many({})

    def findItem(self, itemID):
        item = self.db.find_one({"itemID": itemID})
        if item: item['itemImg'] = "../../" + item['itemImg'][4:]
        return item
    
    def createItem(self, owner, name, price, category, info, image_path, pickup):
        itemID = randomID(IDLENGTH)
        while (self.db.find_one({"itemID": itemID})): itemID = randomID(IDLENGTH)
        newItem = Item(itemID, owner, name, price, category, info, image_path, pickup)
        self.db.insert_one(newItem.__dict__)
        return "Info: New Item Added"

    def deleteItem(self, itemID):
        self.db.delete_one({"itemID": itemID})

    def getItemList(self, user="", cate="", maxprice="", minprice="", search=""):
        selection = {}
        if user != "": selection["itemOwner"] = user
        if cate != "": selection["itemCate"] = cate
        if maxprice != "" and minprice != "": selection["itemPrice"] = {"$lte": int(maxprice), "$gte": int(minprice)}
        elif maxprice != "" and minprice == "": selection["itemPrice"] = {"$lte": int(maxprice)}
        elif maxprice == "" and minprice != "": selection["itemPrice"] = {"$gte": int(minprice)}
        if search != "": selection["itemName"] = {'$regex': search}
        # print(selection)
        itemList = self.db.find(selection)
        itemInfo = {}
        counter = 0
        for item in itemList:
            itemInfo[str(counter)] = item
            itemInfo[str(counter)]['itemImg'] = "../../" + itemInfo[str(counter)]['itemImg'][4:]
            counter += 1
        return itemInfo
    
    def reserveItem(self, itemID, reservedBy):
        now = datetime.now()
        time = now.strftime("%Y.%m.%d %H:%M")
        self.db.update_one({"itemID": itemID}, {'$set': {'itemReserve': reservedBy, 'itemStatus': 'Reserved', 'itemReserveTime': time}})
    
    def dealItem(self, itemID):
        self.db.update_one({"itemID": itemID}, {'$set': { 'itemStatus': 'Sold'}})
    
    def denyItem(self, itemID):
        self.db.update_one({"itemID": itemID}, {'$set': { 'itemStatus': 'Available'}})

class OrderDB():
    def __init__(self, db):
        self.db = db["order"]

class RequestDB():
    def __init__(self, db):
        self.db = db["request"]

    def cleardb(self):
        self.db.delete_many({})

    def findRequest(self, requestID):
        return self.db.find_one({"requestID": requestID})

    def soldRequest(self, requestID, itemID):
        self.db.update_one({"requestID": requestID}, {'$set': {'requestDeal': itemID, 'requestSold': True}})
        return self.db.find_one({"requestID": requestID})
    
    def createRequest(self, user, info):
        requestID = randomID(IDLENGTH)
        while (self.db.find_one({"requestID": requestID})): requestID = randomID(IDLENGTH)
        now = datetime.now()
        time = now.strftime("%Y.%m.%d %H:%M")
        newRequest = Request(requestID, user, info, time)
        self.db.insert_one(newRequest.__dict__)
        return "Info: New Request Added"

    def getRequestList(self, user="", noSold=False):
        selection = {}
        if user != "": selection["requestUser"] = user
        requestList = self.db.find(selection).sort('_id', -1) #.limit(10)
        requestInfo = {}
        counter = 0
        for request in requestList:
            if request["requestSold"] and noSold: continue
            requestInfo[str(counter)] = request
            counter += 1
        return requestInfo
    
    def addRequestItemList(self, requestID, itemID):
        request = self.findRequest(requestID)
        request["requestItemList"].append(itemID)
        self.db.update_one({"requestID": requestID}, {'$set': {'requestItemList': request["requestItemList"]}})

    def dealRequestItem(self, requestID, itemID):
        request = self.findRequest(requestID)
        item = itemdb.findItem(itemID)
        self.db.update_one({"requestID": requestID}, {'$set': {'requestItemList': [item], 'requestSold': True}})
    
    def declineRequestItem(self, requestID, itemID):
        request = self.findRequest(requestID)
        request["requestItemList"].remove(itemID)
        self.db.update_one({"requestID": requestID}, {'$set': {'requestItemList': request["requestItemList"]}})
    
class ChatDB():
    def __init__(self, db):
        self.db = db["chat"]

    def cleardb(self):
        self.db.delete_many({})

    def findChatByBuyer(self, itemID, buyerEmail):
        return self.db.find_one({"chatItem": itemID, "chatBuyer": buyerEmail})
    
    def findChatByOwner(self, itemID, ownerEmail):
        return self.db.find_one({"chatItem": itemID, "chatOwner": ownerEmail})
    
    def findChatByID(self, chatID):
        return self.db.find_one({"chatID": chatID})
    
    def createChat(self, itemID, buyerEmail):
        chatID = randomID(IDLENGTH)
        while (self.db.find_one({"chatID": chatID})): chatID = randomID(IDLENGTH)
        now = datetime.now()
        time = now.strftime("%Y.%m.%d %H:%M")
        item = itemdb.findItem(itemID)
        newChat = Chat(chatID, itemID, item["itemOwner"], buyerEmail, time)
        self.db.insert_one(newChat.__dict__)
        return self.db.find_one({"chatID": chatID})
    
    def sendChat(self, itemID, buyerEmail, ownerEmail, chattxt, type="buyer"):
        chat = self.findChatByBuyer(itemID, buyerEmail)
        print(itemID, buyerEmail, chat["chatInfo"])
        now = datetime.now()
        time = now.strftime("%Y.%m.%d %H:%M")
        if type == "buyer":
            chat["chatInfo"].append({"sendBy": buyerEmail, "sendTo": ownerEmail, "sendTxt": chattxt, "sendTime": time})
        if type == "owner":
            chat["chatInfo"].append({"sendBy": ownerEmail, "sendTo": buyerEmail, "sendTxt": chattxt, "sendTime": time})
        self.db.update_one({"chatItem": itemID, "chatBuyer": buyerEmail}, {'$set': {'chatInfo': chat["chatInfo"]}})

    def getChatList(self, user):
        chatOwnerList = self.db.find({"chatOwner": user})
        chatBuyerList = self.db.find({"chatBuyer": user})
        chatInfo = {}
        counter = 0
        for chat in chatOwnerList:
            itemID = chat["chatItem"]
            item = itemdb.findItem(itemID)
            chatInfo[str(counter)] = item
            chatInfo[str(counter)]['itemImg'] = "../../" + chatInfo[str(counter)]['itemImg'][4:]
            for k, v in chat.items(): chatInfo[str(counter)][k] = v
            chatInfo[str(counter)]["sendTo"] = chat["chatBuyer"]
            counter += 1
        for chat in chatBuyerList:
            itemID = chat["chatItem"]
            item = itemdb.findItem(itemID)
            chatInfo[str(counter)] = item
            chatInfo[str(counter)]['itemImg'] = "../../" + chatInfo[str(counter)]['itemImg'][4:]
            for k, v in chat.items(): chatInfo[str(counter)][k] = v
            chatInfo[str(counter)]["sendTo"] = chat["chatOwner"]
            counter += 1
        return chatInfo
    
class BargainDB():
    def __init__(self, db):
        self.db = db["bargain"]

    def cleardb(self):
        self.db.delete_many({})

    def findBargainByBuyer(self, itemID, buyerEmail):
        return self.db.find_one({"bargainItem": itemID, "bargainFrom": buyerEmail})
    
    def findBargainByItem(self, itemID):
        return self.db.find({"bargainItem": itemID})

    def findBargainList(self, buyerEmail):
        return self.db.find({"bargainFrom": buyerEmail})
    
    def createBargain(self, itemID, buyerEmail):
        now = datetime.now()
        time = now.strftime("%Y.%m.%d %H:%M")
        newB = Bargain(buyerEmail, itemID, time)
        self.db.insert_one(newB.__dict__)
        return self.db.find_one({"bargainItem": itemID, "bargainFrom": buyerEmail})
    
    def sendBargain(self, itemID, buyerEmail, userEmail, price, notes):
        bargain = self.findBargainByBuyer(itemID, buyerEmail)
        now = datetime.now()
        time = now.strftime("%Y.%m.%d %H:%M")
        bargain["bargainInfo"].append({"sendBy": userEmail, "sendTime": time, "price": price, "notes": notes, "Status": "Pending"})
        self.db.update_one({"bargainItem": itemID, "bargainFrom": buyerEmail}, {'$set': {'bargainInfo': bargain["bargainInfo"]}})

    def replyBargain(self, itemID, buyerEmail, userEmail, status, notes, index):
        bargain = self.findBargainByBuyer(itemID, buyerEmail)
        now = datetime.now()
        time = now.strftime("%Y.%m.%d %H:%M")
        bargain["bargainInfo"][index]["Status"] = status
        bargain["bargainInfo"].insert(index + 1, {"sendBy": userEmail, "sendTime": time, "notes": notes})
        self.db.update_one({"bargainItem": itemID, "bargainFrom": buyerEmail}, {'$set': {'bargainInfo': bargain["bargainInfo"]}})


    def checkTime(self, bargain):
        for b in bargain["bargainInfo"]:
            if "Status" in b and b["Status"] == "Pending" and datetime.now() - datetime.strptime(b["sendTime"], "%Y.%m.%d %H:%M") > timedelta(days=1):
                b["Status"] = "Unsolved"
        self.db.update_one({"bargainItem": bargain['bargainItem'], "bargainFrom": bargain['bargainFrom']}, {'$set': {'bargainInfo': bargain["bargainInfo"]}})
    
class StoryDB():
    def __init__(self, db):
        self.db = db["story"]

    def cleardb(self):
        self.db.delete_many({})
    
    def createStory(self, itemID, userEmail, img, intro):
        storyID = randomID(IDLENGTH)
        while (self.db.find_one({"storyID": storyID})): storyID = randomID(IDLENGTH)
        now = datetime.now()
        time = now.strftime("%Y.%m.%d %H:%M")
        newStory = Story(storyID, itemID, userEmail, time, img, intro)
        self.db.insert_one(newStory.__dict__)
        return self.db.find_one({"storyID": storyID})
    
    def getStoryList(self, user=""):
        selection = {}
        if user != "": selection["storyUser"] = user
        storyList = self.db.find(selection).sort('_id', -1)
        storyInfo = {}
        counter = 0
        for story in storyList:
            item = itemdb.findItem(story['storyItem'])
            storyInfo[str(counter)] = story
            storyInfo[str(counter)]['storyImg'] = "../../" + storyInfo[str(counter)]['storyImg'][4:]
            storyInfo[str(counter)]["userName"] = accountdb.findUserName(story['storyUser'])
            storyInfo[str(counter)]["itemName"] = item['itemName']
            counter += 1
        return storyInfo
    
db = connection("test")
accountdb = AccountDB(db)
itemdb = ItemDB(db)
orderdb = OrderDB(db)
requestdb = RequestDB(db)
chatdb = ChatDB(db)
bargaindb = BargainDB(db)
storydb = StoryDB(db)