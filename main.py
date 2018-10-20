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
        log_in_template = jinja_current_directory.get_template('templates/login-page.html')
        request_handler.response.write(log_in_template.render(dict))
        print 'transaction halted because user is not logged in'
        return None

    # at this point, the user is logged into google
    # now let's make sure that user has been logged into our site
    # aka do we have their Google ID in OUR model (which is called User)?
    # user (appengine) vs User (our own Model). Definitely not confusing
    existing_user = User.get_by_id(user.user_id())

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
        print api.get_book(self, 1521919208)

class SellPage(webapp2.RequestHandler):
    def get(self):
        sell_template = jinja_env.get_template("templates/sell.html")
        # Ideally, users choose to add or remove a book to sell
        # If removing, <some functionality>
        # If adding, some way to autopopulate title, author, and edition boxes!

        # show current books that you're trying to sell?
        self.response.write(sell_template.render())

    # this places a form in a space for the user to upload an image
    def submit_form(request):
        if request.method == 'POST':
            form = Form(request.POST)
            if not form.has_changed():
                self.response.write("Please fill out all fields before submitting.")
                # Generate Error

    def post(self):
        condition = self.request.get("condition")
        price = self.request.get("price")

        # upload photo
        # submit and save to database
        our_user = get_logged_in_user(self)

        new_book = Book(
            isbn = self.request.get("isbn"),
            condition = self.request.get("condition"),
            image_model = 1 )
        new_book.put()
        # This below is BS. idk how to add a new object to the StructuredProperty(Book, repeated = True)
        our_user.current.append(new_book)

        self.response.write(sell_template.render())

class BuyPage(webapp2.RequestHandler):
    def post(self):
        buy_template = jinja_env.get_template("templates/buy.html")
        buy_page_dict = {}

        this_book_isbn = 123456789
        # the user's isbn input

        # hopefully this will return a list in condition order
        # I can change out what the .order() is with String.format?!

        # how we're sorting the order
        # condition, -condition, price, -price
        sort_order = self.request.get('how_to_sort')

        q = db.Query(Book)
        book_matches = q.filter('isbn=', this_book_isbn).order('sort_order').fetch()

        # pretty sure I pass in a dictionary through the render()
        self.response.write(buy_template.render(book_matches))

class ResultsPage(webapp2.RequestHandler):
    def get(self):
        try:
            results_page = jinja_env.get_template("templates/main.html")
            self.response.write(results_page.render())
        except Exception as e:
            print e
            self.redirect("/")

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
    ('/sell', SellPage),
    ('/buy', BuyPage),
    ('/results', ResultsPage),
    ('/img', ImagePage),
    ('/test', TestPage),
], debug=True)
