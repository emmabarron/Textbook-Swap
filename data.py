from google.appengine.ext import ndb

class Book(ndb.Model):
    isbn = ndb.IntegerProperty(required=True)
    condition = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty(required=True)
    author = ndb.StringProperty()
    edition = ndb.IntegerProperty()

class UserInfo(ndb.Model):
    # nice goal - could make these not required
    # then if someone doesn't give a name, we use
    # the gmail's name
    firstName = ndb.StringProperty(required=True)
    lastName = ndb.StringProperty(required=True)

    # stretch goal stuff
    # these will make arrays of book objects
    bought = ndb.StructuredProperty(Book, repeated=True)
    sold = ndb.StructuredProperty(Book, repeated=True)
    current = ndb.StructuredProperty(Book, repeated=True)
