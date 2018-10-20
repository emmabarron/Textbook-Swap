from google.appengine.ext import ndb
import time
class UserInfo(ndb.Model):
    longitude = ndb.StringProperty(required=True)
    latitude = ndb.StringProperty(required=True)
    address = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(required=True, auto_now_add=True)
