# Imports
import os
import json
import jinja2
import webapp2
import urllib
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.api import images
from data import UserInfo
from data import Book
from data import Image
import api

jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape = True,
)

# gets current logged-in user
# so it is easy to access their data on each new page
# request_handler is key for self, but since this method isn't in a class
# that makes it very hard to call self xD
def get_logged_in_user(request_handler):
    # gets current user via a method defined in google app engine
    user = users.get_current_user()

    # if this user doesn't exist (aka no one is signed into Google)
    if not user:
        # send them to Google log-in url
        dict = {
            'log_in_url' : users.create_login_url('/')
        }
        # put that Google log-in link on the page and get them in!
        log_in_template = jinja_env.get_template('templates/login-page.html')
        request_handler.response.write(log_in_template.render(dict))
        print 'transaction halted because user is not logged in'
        return None

    # at this point, the user is logged into google
    # now let's make sure that user has been logged into our site
    # aka do we have their Google ID in OUR model (which is called User)?
    # user (appengine) vs User (our own Model). Definitely not confusing
    existing_user = UserInfo.get_by_id(user.user_id())

    # if this person is not a user in our database, throw an error
    if not existing_user:
        print 'transaction halted because user not in database'
        request_handler.error(500)
        return None

    # otherwise if they exist in both Google and our site, let's return them
    # now we can easily access their information
    return existing_user

class GreetingsPage(webapp2.RequestHandler):
    def get(self):
        home_template = jinja_env.get_template("templates/main.html")
        self.response.write(home_template.render()) # Home Page

class LoginPage(webapp2.RequestHandler):
        def get(self):
        login_template = \
                jinja_current_directory.get_template('templates/login-page.html')
        people_template = jinja_current_directory.get_template('templates/people-page.html')
        home_template = jinja_current_directory.get_template('templates/home-page.html')
        login_dict = {}
        name = ""
        user = users.get_current_user()

        # if the user is logged with Google
        if user:
            # magical users method from app engine xD
            email_address = user.nickname()
            # uses User (model obj) method to get the user's Google ID.
            # hopefully it returns something...
            our_site_user = User.get_by_id(user.user_id())
            #dictionary - this gives the sign-out link
            signout_link_html = '<a href="%s">sign out</a>' % (users.create_logout_url('/'))
            signout_link = users.create_logout_url('/')

            # if the user is logged in to both Google and us
            if our_site_user:
                sign_out_dict = {'logout_link' : signout_link, 'name' : our_site_user.name, 'email_address' : email_address}
                self.response.write(home_template.render(sign_out_dict))

              # If the user is logged into Google but never been to us before..
              # if we want to fix OUR login page, this is where
            else:
                # self.response.write('''
                #  Welcome to our site, %s!  Please sign up! <br>
                #  <form method="post" action="/login">
                #  <input type="text" name="first_name">
                #  <input type="text" name="last_name">
                #  <input type="submit">
                #  </form><br> %s <br>
                #  ''' % (email_address, signout_link_html))
                self.response.write(login_template.render())

        # Otherwise, the user isn't logged in to Google or us!
        else:
            self.response.write('''
                Please log in to Google to use our site! <br>
                <a href="%s">Sign in</a>''' % (
                  users.create_login_url('/login')))

    def post(self):
        user = users.get_current_user()
        if not user:
            # You shouldn't be able to get here without being logged in to Google
            self.error(404)
            return
        our_user = User(
            email=user.nickname(),     # current user's email
            id=user.user_id(),         # current user's ID number
            name=self.request.get("first_name") + " " + self.request.get("last_name")
            )
        our_user.put()
        wel_dict = {'welcome': 'Thanks for signing up, %s!' %
            our_user.name}

        home_template = jinja_current_directory.get_template('templates/home-page.html')
        self.response.write(home_template.render(wel_dict))

class SellPage(webapp2.RequestHandler):
    def get(self):
        sell_template = jinja_env.get_template("templates/sell.html")
        
        # show current books the user is currently trying to sell
        # also shows what the user has sold
        current_user = get_logged_in_user(self)
        sell_page_dict = {}
        if current_user.selling:
            sell_page_dict['selling'] = current_user.selling
        if current_user.sold:
            sell_page_dict['sold'] = current_user.sold

        self.response.write(sell_template.render(sell_page_dict))

        # Ideally, users choose to add or remove a book to sell
        # If removing, <some functionality>
        # If adding, some way to autopopulate title, author, and edition boxes!
        
    def post(self):
        condition = self.request.get("condition")
        isbn = self.request.get("isbn")
        price = self.request.get("price")

        # upload photo
        # submit and save to database
        our_user = get_logged_in_user(self)
        book_json = api.get_book(isbn)

        # make a new book object
        new_book = Book(
            isbn = isbn,
            # run the API to auto-fill the other spaces in the form
            # that would be json, pretty sure
            condition = condition,
            is_selling = True,
            price = price,
            image_model = 1)

        # add the book to the user's selling list
        new_book.put()
        # This below is BS. idk how to add a new object to the StructuredProperty(Book, repeated = True)
        our_user.selling.append(new_book)

        # When the user submits, we'll have the page redirect?
        # Emma can't remember the control flow here - Shruthi!
        # self.redirect("/profile")

# Emma thinks it's done, just make sure the html lines up with this!
class ResultsPage(webapp2.RequestHandler):
    def post(self):
        current_user = get_logged_in_user(self)
        buy_template = jinja_env.get_template("templates/results.html")
        buy_page_dict = {}

        # books that the user has bought
        if current_user.bought:
            buy_page_dict['bought'] = current_user.bought

        this_book_isbn = self.request.get('isbn')
        # the user's isbn input

        # hopefully this will return a list in condition order
        # I can change out what the .order() is with String.format?!

        # how we're sorting the order
        # "condition"     condition ascending
        # "-condition"    condition descending
        # "price"         price ascending
        # "-price"        price descending
        sort_order = self.request.get('how_to_sort')

        q = db.Query(Book)
        book_matches = q.filter('selling', True).filter('isbn=', this_book_isbn).order(sort_order).fetch()
        buy_page_dict['book_matches'] = book_matches

        self.response.write(buy_template.render(buy_page_dict))

class ImagePage(webapp2.RequestHandler):
    def get(self):
        # to do this, we need to have a "/img?id=" + str(img_id)
        # the self.request.get('id') works for stuff after ?
        img_id = self.request.get('id')

        if not img_id:
            return self.error(400)
        img_item = Image.get_by_id(long(img_id))

        if not img_item:
            return self.error(404)
        img_in_binary = images.Image(img_item.image)
        img_in_binary.resize(200, 200)
        some_img = img_in_binary.execute_transforms(output_encoding=images.JPEG)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(some_img)

    def post(self):
        avatar = self.request.get('image')

        avatar = images.resize(avatar, 500, 500)
        current_user = get_logged_in_user(self)

        this_image = Image(image=avatar)
        img_id = this_image.put()
        current_user.image_model = img_id
        current_user.put()
        self.redirect('/sell')

class TestPage(webapp2.RequestHandler):
    def get(self):
        # home_template = jinja_env.get_template("templates/main.html")
        self.response.write(api.get_book(self, 1521919208)) # Home Page

app = webapp2.WSGIApplication([
    ('/', GreetingsPage),
    ('/login', LoginPage),
    ('/sell', SellPage),
    ('/results', ResultsPage),
    ('/img', ImagePage),
    ('/test', TestPage),
], debug=True)
