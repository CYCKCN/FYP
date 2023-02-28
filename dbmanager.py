from db import accountdb
from utils import Account

if __name__ == '__main__':
    accountdb.cleardb()
    newAccount = Account("super", "life2", "00001", auth="STAFF")
    accountdb.signup("super", "life2", "00001", auth="STAFF")