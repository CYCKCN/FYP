import os
import pathlib

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests

from flask_login import UserMixin
from flask_wtf import FlaskForm
import wtforms
import random
from functools import wraps
from wtforms.validators import InputRequired, Email, Length, Regexp
from flask import Blueprint, request, session, redirect, render_template, url_for
# from google.cloud import exceptions, ndb, storage

time = ["0800", "0815", "0830", "0845", "0900", "0915", "0930", "0945", "1000", "1015", "1030", "1045", \
        "1100", "1115", "1130", "1145", "1200", "1215", "1230", "1245", "1300", "1315", "1330", "1345", \
        "1400", "1415", "1430", "1445", "1500", "1515", "1530", "1545", "1600", "1615", "1630", "1645", \
        "1700", "1715", "1730", "1745", "1800"]

UNIADDR = {"HKUST": "ust.hk", "CUHK": "cuhk.edu.hk"}

IDLENGTH = 12 
UPLOAD_FOLDER = 'app/static/data'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

CATEGORY = ['Electronics', 'Clothing', 'Personal Care', 'Furnitures', 'Toys', 'Sports', "Others"]
CONDITION = ['Brand New', 'Like New', 'Lightly Used', 'Well Used', 'Heavily Used']
PRICERANGE = ["Less than 50", "Between 50 - 100", "Between 100 - 200", "More than 200"]

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "332552845298-u5ejfour55akd8q2d73i2be5odrmah07.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

# ds_client = ndb.Client()
# gcs_client = storage.Client()
# _, PROJECT_ID = google.auth.default()
# BUCKET = '%s.appspot.com' % PROJECT_ID

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://life2.space/auth/callback"
)

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
    def __init__(self, email):
        self.accountEmail = email # "university email"

class Item(object):
    def __init__(self, id, owner, name, price, category, condition, info, image_path, pickup_location, time, status="Available", reservedby="", reservedtime=''):
        self.itemID = id # random 12 numbers
        self.itemTime = time
        self.itemOwner = owner # "33872" / "-1"
        self.itemName = name
        self.itemPrice = float(price)
        self.itemCate = category
        self.itemCond = condition
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
    def __init__(self, id, user, info, time):
        self.requestID = id # random 12 numbers
        self.requestUser = user # "33872" / "-1"
        self.requestInfo = info
        self.requestTime = time
        self.requestSold = False
        self.requestDeal = None
        self.requestItemList = []

class Chat(object):
    def __init__(self, chatID, itemID, ownerEmail, buyerEmail, created_time, chatInfo=[]):
        self.chatID = chatID
        self.chatItem = itemID
        self.chatOwner = ownerEmail
        self.chatBuyer = buyerEmail
        self.chatCreated = created_time
        self.chatInfo = chatInfo

class Bargain(object):
    def __init__(self, buyerEmail, itemID, created_time, bargainPrice=None, bargainInfo=[]):
        self.bargainFrom = buyerEmail
        self.bargainItem = itemID
        self.bargainCreated = created_time
        self.bargainPrice = bargainPrice
        self.bargainDeal = False
        self.bargainInfo = bargainInfo # [(sendby, create time, notes)]

class Story(object):
    def __init__(self, storyID, itemID, useremail, created_time, image_path, intro):
        self.storyID = storyID
        self.storyItem = itemID
        self.storyUser = useremail
        self.storyTime = created_time
        self.storyImg = image_path
        self.storyIntro = intro

class RequestForm(FlaskForm):
    title = wtforms.StringField('Name', validators=[Length(max=30)])
    info = wtforms.StringField('Description', validators=[Length(max=5000)])

class StoryForm(FlaskForm):
    info = wtforms.StringField('Description', validators=[Length(max=5000)])

class ItemForm(FlaskForm):
    name = wtforms.StringField('Name', validators=[Length(max=30)])
    price = wtforms.FloatField('Price')
    description = wtforms.TextAreaField('Description')
    pickup = wtforms.StringField('Pick-Up', validators=[Length(max=30)])

def randomID(length):
    id = str()
    for i in range(length): id += str(random.randint(0, 9))
    return id

def buttonCheck(form):
    home = form.get('Home')
    market = form.get('Market')
    demand = form.get('Demand')
    piazza = form.get('Piazza')
    login = form.get('Login')
    signup = form.get('Signup')
    profile = form.get('Profile')
    chat = form.get('Chat')

    # print(home)
    if home == "Home": 
        return redirect(url_for('market.home'))
    
    if market == "Market": 
        return redirect(url_for('market.home'))

    if demand == "Demand": 
        return redirect(url_for('demand.home'))
    
    if piazza == "Piazza": 
        return redirect(url_for('piazza.home'))
    
    if login == "Login": 
        return redirect(url_for('auth.google_login'))
    
    if signup == "Signup": 
        return redirect(url_for('auth.signup'))

    if profile == "Profile": 
        return redirect(url_for('life.profile'))
    
    if chat == "Chat":
        return redirect(url_for('life.chat'))