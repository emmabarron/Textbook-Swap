from google.appengine.ext import ndb

class Image(ndb.Model):
    image = ndb.BlobProperty()

class UserInfo(ndb.Model):
    # nice goal - could make these not required
    # then if someone doesn't give a name, we use
    # the gmail's name
    email = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)

class Book(ndb.Model):
    isbn = ndb.IntegerProperty(required=True)
    condition = ndb.StringProperty(required=True)
    condition_num = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty()
    author = ndb.StringProperty()
    edition = ndb.IntegerProperty()
    price = ndb.FloatProperty(required = True)
    owner = ndb.KeyProperty(kind=UserInfo)
    is_selling = ndb.BooleanProperty(default=True)
    image_model = ndb.KeyProperty(kind=Image)
