
from pymongo.mongo_client import MongoClient
from utils import Account, User, Item, randomID, IDLENGTH

from werkzeug.security import generate_password_hash, check_password_hash
    
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

    def findUser(self, accountID):
        return self.db.find_one({"accountID": accountID})
    
    def findUserName(self, accountID):
        account = self.db.find_one({"accountID": accountID})
        if account is None: return "Err: Not Registered!"
        return account["accountName"]
    
    def login(self, accountID, accountPw, auth):
        account = self.db.find_one({"accountID": accountID})
        if account is None: 
            return "Err: Not Registered!"
        elif check_password_hash(account["accountPw"], accountPw) == False:
            return "Err: Wrong Password!"
        elif account["accountAuth"] != auth:
            return "Err: You Are Not Authorized!"
        else:
            return "Info: Login successfully!"
        
    def signup(self, accountName, accountPw, accountID, auth="USER"):
        if self.db.find_one({"accountName": accountName}):
            return "Err: Account Exists!"
        newAccount = Account(accountName, generate_password_hash(accountPw), accountID, auth=auth)
        self.db.insert_one(newAccount.__dict__)
        return "Info: Register USER Account Successfully"

class ItemDB():
    def __init__(self, db):
        self.db = db["item"]

    def cleardb(self):
        self.db.delete_many({})

    def findItem(self, itemID):
        return self.db.find_one({"itemID": itemID})
    
    def createItem(self, owner, name, price, category, info, image_path):
        itemID = randomID(IDLENGTH)
        while (self.db.find_one({"itemID": itemID})): itemID = randomID(IDLENGTH)
        newItem = Item(itemID, owner, name, price, category, info, image_path)
        self.db.insert_one(newItem.__dict__)
        return "Info: New Item Added"


class OrderDB():
    def __init__(self, db):
        self.db = db["order"]

db = connection("LIFE2")
accountdb = AccountDB(db)
itemdb = ItemDB(db)
orderdb = OrderDB(db)