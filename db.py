
from pymongo.mongo_client import MongoClient
from utils import Account, User, Item, Request, Chat, randomID, IDLENGTH, UNIADDR

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
    
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
    
    def findUserName(self, accountEmail):
        account = self.db.find_one({"accountEmail": accountEmail})
        if account is None: return "Err: Not Registered!"
        return account["accountName"]
    
    def login(self, accountEmail, accountPw):
        account = self.db.find_one({"accountEmail": accountEmail})
        if account is None: 
            return "Err: Not Registered!"
        elif check_password_hash(account["accountPw"], accountPw) == False:
            return "Err: Wrong Password!"
        else:
            return "Info: Login successfully!"
        
    def signup(self, accountName, accountPw, accountEmail, accountUni):
        # print(accountName, accountPw, accountEmail, accountUni)
        if self.db.find_one({"accountEmail": accountEmail}):
            return "Err: Account Exists!"
        # print(UNIADDR[accountUni])
        if UNIADDR[accountUni] not in accountEmail:
            return "Err: Email Invalid!"
        newAccount = Account(accountName, generate_password_hash(accountPw), accountEmail, accountUni, tel="", intro="")
        self.db.insert_one(newAccount.__dict__)
        return "Info: Register USER Account Successfully"

class ItemDB():
    def __init__(self, db):
        self.db = db["item"]

    def cleardb(self):
        self.db.delete_many({})

    def findItem(self, itemID):
        item = self.db.find_one({"itemID": itemID})
        item['itemImg'] = "../../" + item['itemImg'][8:]
        return item
    
    def createItem(self, owner, name, price, category, info, image_path, pickup):
        itemID = randomID(IDLENGTH)
        while (self.db.find_one({"itemID": itemID})): itemID = randomID(IDLENGTH)
        newItem = Item(itemID, owner, name, price, category, info, image_path, pickup)
        self.db.insert_one(newItem.__dict__)
        return "Info: New Item Added"

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
            itemInfo[str(counter)]['itemImg'] = "../../" + itemInfo[str(counter)]['itemImg'][8:]
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
    
    def createRequest(self, user, title, category, info):
        requestID = randomID(IDLENGTH)
        while (self.db.find_one({"requestID": requestID})): requestID = randomID(IDLENGTH)
        now = datetime.now()
        time = now.strftime("%Y.%m.%d %H:%M")
        newRequest = Request(requestID, user, title, category, info, time)
        self.db.insert_one(newRequest.__dict__)
        return "Info: New Request Added"

    def getRequestList(self, user=""):
        selection = {}
        if user != "": selection["requestUser"] = user
        requestList = self.db.find(selection).sort('_id', -1).limit(10)
        requestInfo = {}
        counter = 0
        for request in requestList:
            # print(request)
            requestInfo[str(counter)] = request
            requestInfo[str(counter)]["userName"] = accountdb.findUserName(request['requestUser'])
            counter += 1
        return requestInfo
    
    def addRequestItemList(self, requestID, itemID):
        request = self.findRequest(requestID)
        item = itemdb.findItem(itemID)
        request["requestItemList"].append(item)
        self.db.update_one({"requestID": requestID}, {'$set': {'requestItemList': request["requestItemList"]}})

    def dealRequestItem(self, requestID, itemID):
        request = self.findRequest(requestID)
        item = itemdb.findItem(itemID)
        self.db.update_one({"requestID": requestID}, {'$set': {'requestItemList': [item]}})
    
    def declineRequestItem(self, requestID, itemID):
        request = self.findRequest(requestID)
        item = itemdb.findItem(itemID)
        request["requestItemList"].remove(item)
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
            chatInfo[str(counter)]['itemImg'] = "../../" + chatInfo[str(counter)]['itemImg'][8:]
            for k, v in chat.items(): chatInfo[str(counter)][k] = v
            chatInfo[str(counter)]["sendTo"] = chat["chatBuyer"]
            counter += 1
        for chat in chatBuyerList:
            itemID = chat["chatItem"]
            item = itemdb.findItem(itemID)
            chatInfo[str(counter)] = item
            chatInfo[str(counter)]['itemImg'] = "../../" + chatInfo[str(counter)]['itemImg'][8:]
            for k, v in chat.items(): chatInfo[str(counter)][k] = v
            chatInfo[str(counter)]["sendTo"] = chat["chatOwner"]
            counter += 1
        return chatInfo

db = connection("LIFE2")
accountdb = AccountDB(db)
itemdb = ItemDB(db)
orderdb = OrderDB(db)
requestdb = RequestDB(db)
chatdb = ChatDB(db)