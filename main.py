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

jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape = True,
)

class GreetingsPage(webapp2.RequestHandler):
    def get(self):
        home_template = jinja_env.get_template("templates/main.html")
        self.response.write(home_template.render()) # Home Page

class SellPage(webapp2.RequestHandler):
    def get(self):
        sell_template = jinja2_env.get_template("templates/sell.html")
        self.response.write(sell_template.render())

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
        # the self.request.get('id') works fro stuff after ?
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

        # send it back to the page!
        # OMG if this works I can use it in my peoples page too!?!
        # like, I could send the image in binary over? Or I could have each user call this method?
        # they each have their own image IDs
        # and then that ID can be used to build like a dictionary? (Or will that mess it up)
    def post(self):
        avatar = self.request.get('image')

        avatar = images.resize(avatar, 500, 500)
        current_user = get_logged_in_user(self)

        this_image = Image(image=avatar)
        img_id = this_image.put()
        current_user.image_model = img_id
        current_user.put()
        self.redirect('/info_update')

app = webapp2.WSGIApplication([
    ('/', GreetingsPage),
    ('/sell', SellPage),
    ('/results', ResultsPage),
    ('/img', ImagePage)
], debug=True)
