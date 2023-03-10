from flask_login import UserMixin
from flask_wtf import FlaskForm
import wtforms
import random
from wtforms.validators import InputRequired, Email, Length, Regexp
from flask import Blueprint, request, redirect, render_template, url_for

time = ["0800", "0815", "0830", "0845", "0900", "0915", "0930", "0945", "1000", "1015", "1030", "1045", \
        "1100", "1115", "1130", "1145", "1200", "1215", "1230", "1245", "1300", "1315", "1330", "1345", \
        "1400", "1415", "1430", "1445", "1500", "1515", "1530", "1545", "1600", "1615", "1630", "1645", \
        "1700", "1715", "1730", "1745", "1800"]

UNIADDR = {"HKUST": "ust.hk", "CUHK": "cuhk.edu.hk"}

IDLENGTH = 12 
UPLOAD_FOLDER = 'webpage/static/data'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

CATEGORY = ["toy", "electronics"]
PRICERANGE = ["Less than 50", "Between 50 - 100", "Between 100 - 200", "More than 200"]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class User(UserMixin):
    def __init__(self, email):
        self.email = email

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.email
    
class Account(object):
    def __init__(self, name, password, email, uni, tel, intro):
        self.accountName = name # "name"
        self.accountEmail = email # "university email"
        self.accountUni = uni
        self.accountPw = password # "examplePW"
        self.accountTel = tel
        self.accountIntro = intro

class Item(object):
    def __init__(self, id, owner, name, price, category, info, image_path, pickup_location, status="Available", reservedby="", reservedtime=''):
        self.itemID = id # random 12 numbers
        self.itemOwner = owner # "33872" / "-1"
        self.itemName = name
        self.itemPrice = float(price)
        self.itemCate = category
        self.itemInfo = info
        self.itemImg = image_path
        self.itemPickUp = pickup_location
        self.itemStatus = status
        self.itemReserve = reservedby
        self.itemReserveTime = reservedtime

# class Order(object):
#     def __init__(self, id, stime, etime, orderType="SELL", itemid=None, orderStatus="R"):
#         self.orderID = id # "3387220221217"
#         self.orderItemID = itemid # None / "3387220221217003"
#         self.orderType = orderType # "SELL" / "BUY"
#         self.orderStartTime = stime # "202212171000"
#         self.orderEndTime = etime # "202212171030"
#         self.orderStatus = orderStatus # "R" -> Reserved / "S" -> Solved

class Request(object):
    def __init__(self, id, user, title, category, info, time):
        self.requestID = id # random 12 numbers
        self.requestUser = user # "33872" / "-1"
        self.requestTitle = title
        self.requestInfo = info
        self.requestCate = category
        self.requestTime = time

class RequestForm(FlaskForm):
    title = wtforms.StringField('Name', validators=[Length(max=30)])
    info = wtforms.StringField('Description', validators=[Length(max=5000)])

class ItemForm(FlaskForm):
    name = wtforms.StringField('Name', validators=[Length(max=30)])
    price = wtforms.FloatField('Price')
    description = wtforms.StringField('Description', validators=[Length(max=30)])
    pickup = wtforms.StringField('Pick-Up', validators=[Length(max=30)])

def randomID(length):
    id = str()
    for i in range(length): id += str(random.randint(0, 9))
    return id

def buttonCheck(form):
    home = form.get('Home')
    sell = form.get('Sell')
    buy = form.get('Request')
    login = form.get('Login')
    signup = form.get('Signup')
    profile = form.get('Profile')
    chat = form.get('Chat')

    # print(home)
    if home == "Home": 
        return redirect(url_for('life.home'))
    
    if sell == "Sell": 
        return redirect(url_for('life.sell'))

    if buy == "Request": 
        return redirect(url_for('life.buy'))
    
    if login == "Login": 
        return redirect(url_for('auth.login'))
    
    if signup == "Signup": 
        return redirect(url_for('auth.signup'))

    if profile == "Profile": 
        return redirect(url_for('life.profile'))
    
    if chat == "Chat":
        return redirect(url_for('life.chat'))